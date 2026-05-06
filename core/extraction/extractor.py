"""
DiagramExtractor — Extrator OCR de diagramas de arquitetura.

Três modos detectados automaticamente:

  LEGEND  — anchors numa coluna vertical na BORDA da imagem (>70% ou <30% X).
             Ex: diagrama Frontend→API→Database com legenda lateral.
             Estratégia: semântico primeiro, proximidade como fallback.

  VERTICAL — anchors em coluna vertical no CENTRO da imagem.
             Ex: diagrama ERP com Interface/Business/Persistance Layer empilhados.
             Estratégia: Y-zone primeiro, semântico como desempate.

  HORIZONTAL — anchors espalhados horizontalmente na mesma faixa Y.
             Ex: diagrama User→Browser→Front-end→Back-end→Databases.
             Estratégia: proximidade euclidiana (cada membro fica abaixo do seu container).
"""

import cv2
import easyocr
import numpy as np
from collections import defaultdict


# ---------------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------------

# Tier 1: palavras que indicam explicitamente uma camada nomeada
LAYER_ANCHOR_WORDS = [
    "layer", "camada",
    "tier", "nivel", "nível",
]

# Tier 2: containers comuns — match EXATO (evita "Database Queries" virar âncora)
CONTAINER_ANCHOR_WORDS = {
    "front-end", "frontend",
    "back-end", "backend",
    "databases", "database",
    "web server", "app server",
    "api gateway",
    "microservice",
    "message queue", "message broker",
    "load balancer", "reverse proxy",
}

# Padrões de label de seta — texto curto descrevendo um fluxo/protocolo.
# Removidos "query/queries" sozinhos pois são ambíguos (podem ser conteúdo
# de banco). Mantemos só combinações típicas de comunicação.
FLOW_PATTERNS = [
    "http request", "http response", "https request", "https response",
    "xmlhttp", "xml http", "ajax", "api call", "rest call",
    "database queries", "database query",
    "send request", "fetch data", "push event", "publish message",
    "rpc call", "grpc call", "websocket",
]

# Termos isolados que SÓ são flow se forem o texto inteiro (ou quase)
FLOW_STANDALONE = {
    "response", "request", "http", "https",
    "fetch", "push", "publish", "subscribe",
}

SKIP_WORDS = {
    "diagrama", "diagram", "architecture", "arquitetura",
    "summary", "layers", "layer legend",
    "sistema de gestão", "erp-adj", "erp",
    "diagrama de arquitetura", "internet",
    "@", "marianabernado",
}

KNOWLEDGE_BASE = {
    "interface":    "user_interface_layer",
    "iu":           "user_interface_layer",
    "ui":           "user_interface_layer",
    "frontend":     "frontend_layer",
    "front-end":    "frontend_layer",
    "react":        "frontend_framework",
    "angular":      "frontend_framework",
    "vue":          "frontend_framework",
    "javascript":   "frontend_framework",
    "html":         "frontend_framework",
    "api":          "api_architecture_style",
    "rest":         "api_architecture_style",
    "graphql":      "api_architecture_style",
    "grpc":         "communication_protocol",
    "http":         "communication_protocol",
    "xml":          "data_format",
    "json":         "data_format",
    "business":     "business_layer",
    "service":      "service_layer",
    "backend":      "service_layer",
    "back-end":     "service_layer",
    "node":         "service_layer",
    "python":       "service_layer",
    "java":         "service_layer",
    "persistence":  "data_access_layer",
    "persistance":  "data_access_layer",
    "orm":          "object_relational_mapping",
    "doctrine":     "php_orm_framework",
    "postgres":     "relational_db",
    "postgresql":   "relational_db",
    "mysql":        "relational_db",
    "sql server":   "database_system",
    "sql":          "relational_db",
    "mongo":        "nosql_db",
    "redis":        "cache_layer",
    "kafka":        "message_broker",
    "rabbitmq":     "message_broker",
    "nginx":        "reverse_proxy",
    "docker":       "containerization",
    "kubernetes":   "orchestration",
    "aws":          "cloud_provider",
    "azure":        "cloud_provider",
    "gcp":          "cloud_provider",
    "auth":         "authentication",
    "cache":        "cache_layer",
    "gateway":      "api_gateway",
}

# Palavras da âncora → palavras que indicam pertencimento de um componente
LAYER_SEMANTIC_MAP = {
    "frontend":     ["frontend", "front-end", "react", "angular", "vue", "next",
                     "svelte", "html", "javascript", "js", "css", "browser", "client"],
    "front":        ["javascript", "html", "css", "react", "angular", "vue",
                     "browser", "ui", "frontend", "front-end"],
    "backend":      ["backend", "back-end", "node", "nodejs", "python", "java",
                     "go", "ruby", "php", "django", "spring", "server", "api"],
    "back":         ["node", "nodejs", "python", "java", "go", "ruby", "php",
                     "backend", "back-end", "server", "api", "service"],
    "api":          ["api", "backend", "back-end", "service", "rest", "graphql",
                     "grpc", "gateway", "microservice", "endpoint", "controller"],
    "data":         ["database", "db", "sql", "postgres", "postgresql", "mysql",
                     "mongo", "mongodb", "redis", "orm", "doctrine", "persistence",
                     "persistance", "storage", "repository"],
    "database":     ["database", "db", "sql", "postgres", "mysql", "mongo",
                     "redis", "oracle", "cassandra"],
    "databases":    ["database", "db", "sql", "postgres", "mysql", "mongo",
                     "redis", "oracle"],
    "persistence":  ["orm", "doctrine", "hibernate", "repository",
                     "database", "db", "sql", "postgres"],
    "persistance":  ["orm", "doctrine", "hibernate", "repository",
                     "database", "db", "sql", "postgres"],
    "business":     ["business", "logic", "rule", "process", "workflow",
                     "service", "manager", "handler", "usecase"],
    "interface":    ["interface", "ui", "iu", "html", "javascript", "user",
                     "view", "screen", "page", "form", "browser"],
    "presentation": ["view", "html", "css", "template", "ui", "screen",
                     "interface", "javascript"],
    "service":      ["service", "backend", "api", "worker", "microservice"],
    "cache":        ["cache", "redis", "memcached"],
    "message":      ["kafka", "rabbitmq", "sqs", "pubsub", "queue", "broker"],
    "web":          ["frontend", "front-end", "backend", "back-end", "browser",
                     "html", "javascript", "server", "http"],
}


# ---------------------------------------------------------------------------
# Helpers OCR
# ---------------------------------------------------------------------------

def _bbox_center(bbox):
    xs = [p[0] for p in bbox]; ys = [p[1] for p in bbox]
    return (sum(xs) / 4, sum(ys) / 4)

def _bbox_rect(bbox):
    xs = [p[0] for p in bbox]; ys = [p[1] for p in bbox]
    return (min(xs), min(ys), max(xs), max(ys))

def _distance(a, b):
    return float(np.linalg.norm(np.array(a) - np.array(b)))

def _is_layer_anchor(text):
    tl = text.lower().strip()
    # Tier 1: qualquer palavra de camada aparece no texto
    if any(w in tl for w in LAYER_ANCHOR_WORDS):
        return True
    # Tier 2: o texto inteiro é exatamente um nome de container
    return tl in CONTAINER_ANCHOR_WORDS

def _is_flow_text(text):
    """
    Detecta texto que é label de seta/fluxo. Critérios:
      1. Contém padrão composto típico (ex: "http request", "database queries")
      2. OU é exatamente um termo standalone (ex: "Response", "HTTP")
      3. Texto curto (< 4 palavras) é mais provável de ser flow
    """
    tl = text.lower().strip()
    # Padrões compostos — match em qualquer parte
    for pat in FLOW_PATTERNS:
        if pat in tl:
            return True
    # Standalone — match exato (texto inteiro é só essa palavra)
    if tl in FLOW_STANDALONE:
        return True
    # Detecta padrão "xmlHttp Response", "AJAX Response", etc.
    words = tl.split()
    if len(words) <= 3 and any(w in tl for w in ["response", "request"]):
        return True
    return False

def _is_skip(text):
    tl = text.lower().strip()
    return any(w in tl for w in SKIP_WORDS)


def _merge_nearby_blocks(blocks, x_gap=55, y_gap=20):
    if not blocks:
        return []
    sorted_b = sorted(blocks, key=lambda b: (b["center"][1], b["center"][0]))
    used = [False] * len(sorted_b)
    merged = []
    for i, bi in enumerate(sorted_b):
        if used[i]:
            continue
        gtexts = [bi["text"]]; grects = [bi["rect"]]; gcents = [bi["center"]]
        used[i] = True
        for j, bj in enumerate(sorted_b):
            if used[j] or i == j:
                continue
            if (abs(bi["center"][1] - bj["center"][1]) <= y_gap and
                    abs(bi["center"][0] - bj["center"][0]) <= x_gap):
                gtexts.append(bj["text"]); grects.append(bj["rect"])
                gcents.append(bj["center"]); used[j] = True
        merged.append({
            "text":   " ".join(gtexts),
            "center": (sum(c[0] for c in gcents) / len(gcents),
                       sum(c[1] for c in gcents) / len(gcents)),
            "rect":   (min(r[0] for r in grects), min(r[1] for r in grects),
                       max(r[2] for r in grects), max(r[3] for r in grects)),
        })
    return merged


# ---------------------------------------------------------------------------
# Semântico
# ---------------------------------------------------------------------------

def _anchor_keywords(anchor_name):
    name_lower = anchor_name.lower()
    keywords = []
    for key, words in LAYER_SEMANTIC_MAP.items():
        if key in name_lower:
            keywords.extend(words)
    return list(set(keywords))

def _semantic_score(component_text, anchor_keywords):
    tl = component_text.lower()
    return sum(1 for kw in anchor_keywords if kw in tl)


# ---------------------------------------------------------------------------
# Detecção de modo
# ---------------------------------------------------------------------------

def _detect_mode(anchors, img_w, img_h):
    """
    Retorna o modo de agrupamento:
      'legend'     — anchors em coluna vertical na BORDA (>70% ou <30% X)
      'vertical'   — anchors em coluna vertical no CENTRO
      'horizontal' — anchors espalhados horizontalmente na mesma faixa Y
      'proximity'  — fallback genérico
    """
    if len(anchors) < 2:
        return "proximity"

    xs  = [a["center"][0] for a in anchors]
    ys  = [a["center"][1] for a in anchors]
    std_x  = float(np.std(xs))
    std_y  = float(np.std(ys))
    mean_x = float(np.mean(xs))

    is_vertical_cluster  = std_x < img_w * 0.10   # anchors têm X parecido
    is_at_edge           = mean_x > img_w * 0.70 or mean_x < img_w * 0.30
    is_horizontal_spread = std_x > img_w * 0.12   # anchors espalhados em X
    is_same_y_level      = std_y < img_h * 0.10   # anchors na mesma altura

    if is_vertical_cluster and is_at_edge:
        return "legend"
    elif is_horizontal_spread and is_same_y_level:
        return "horizontal"
    elif is_vertical_cluster:
        return "vertical"
    else:
        return "proximity"


# ---------------------------------------------------------------------------
# Y-zone (modo vertical)
# ---------------------------------------------------------------------------

def _build_y_zones(anchors):
    sorted_a = sorted(enumerate(anchors), key=lambda x: x[1]["center"][1])
    zones = []
    n = len(sorted_a)
    for k, (orig_idx, anchor) in enumerate(sorted_a):
        yc = anchor["center"][1]
        y_min = -float("inf") if k == 0 else (sorted_a[k-1][1]["center"][1] + yc) / 2
        y_max =  float("inf") if k == n-1 else (yc + sorted_a[k+1][1]["center"][1]) / 2
        zones.append((orig_idx, y_min, y_max))
    return zones

def _assign_by_y_zone(member, zones):
    cy = member["center"][1]
    for orig_idx, y_min, y_max in zones:
        if y_min <= cy <= y_max:
            return orig_idx
    return min(zones, key=lambda z: min(abs(cy - z[1]), abs(cy - z[2])))[0]


# ---------------------------------------------------------------------------
# Clustering de membros (compound components)
# ---------------------------------------------------------------------------

def _rect_gap_xy(r1, r2):
    """
    Gap entre as BORDAS dos retângulos (não centros). Retorna (dx, dy).
    dx = quanto há de espaço horizontal vazio entre eles (0 se sobrepostos)
    dy = quanto há de espaço vertical vazio entre eles (0 se sobrepostos)

    Crítico: distância entre BORDAS distingue
      - texto multilinha na mesma caixa (gap 5-15px)
      - caixas adjacentes (gap 50+px)
    Distância entre CENTROS não distingue (depende do tamanho do texto).
    """
    x10, y10, x11, y11 = r1
    x20, y20, x21, y21 = r2
    dx = max(0, x10 - x21, x20 - x11)
    dy = max(0, y10 - y21, y20 - y11)
    return dx, dy


def _cluster_members(members, max_x_gap=40, max_y_gap=30):
    """
    Clusteriza membros pertencentes à mesma caixa visual usando GAP entre
    bordas dos retângulos OCR.

    Dois textos pertencem ao mesmo cluster se:
      - gap horizontal entre bordas <= max_x_gap (≈ padding lateral)
      - gap vertical entre bordas <= max_y_gap (≈ espaçamento entre linhas)

    Valores padrão calibrados:
      max_y_gap=30: line-height típico de texto multilinha (10-25px)
      max_x_gap=40: tolerância para textos não perfeitamente alinhados em X

    Resolve o problema de "HTML Document Containing only" (rect bottom Y=485)
    e "Javascript Library Subset (min)" (rect top Y=495) — gap real é 10px,
    mas distância entre centros é ~50px (que confundia o algoritmo antigo).
    """
    n = len(members)
    if n == 0:
        return []

    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    for i in range(n):
        for j in range(i + 1, n):
            dx, dy = _rect_gap_xy(members[i]["rect"], members[j]["rect"])
            if dx <= max_x_gap and dy <= max_y_gap:
                union(i, j)

    clusters = defaultdict(list)
    for i in range(n):
        clusters[find(i)].append(i)
    return list(clusters.values())


def _anchors_bounding_box(anchors, img_w, img_h, margin_frac=0.08):
    """
    Calcula o bounding box que contém TODOS os anchors com uma margem.
    Membros fora desse box estão claramente fora da região arquitetural
    desenhada e devem ser descartados (ex: User/Browser fora de Web Server).
    """
    if not anchors:
        return (0, 0, img_w, img_h)
    xs = [a["center"][0] for a in anchors]
    ys = [a["center"][1] for a in anchors]
    mx = img_w * margin_frac
    my = img_h * margin_frac
    return (min(xs) - mx, min(ys) - my, max(xs) + mx, max(ys) + my)


def _point_in_rect(px, py, rect):
    return rect[0] <= px <= rect[2] and rect[1] <= py <= rect[3]


def _cluster_centroid(members, indices):
    """Retorna o centroide (x, y) de um cluster de membros."""
    xs = [members[i]["center"][0] for i in indices]
    ys = [members[i]["center"][1] for i in indices]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


# ---------------------------------------------------------------------------
# Agrupamento principal
# ---------------------------------------------------------------------------

def _group_members(anchors, members, img_w, img_h):
    """
    Agrupamento baseado em CLUSTERS de componentes visuais.

    Estratégia unificada:
      1. Clusteriza membros próximos espacialmente (mesmo X, Y próximo)
         → cada cluster representa uma "caixa visual" do diagrama.
      2. Calcula o centroide do cluster.
      3. Atribui o cluster INTEIRO ao anchor escolhido pela estratégia
         do modo detectado, usando o centroide como referência.

    Garante que membros visualmente agrupados (ex: HTML Document +
    Javascript Library Subset, mesma caixa azul) sempre vão juntos para
    o mesmo grupo, mesmo se um deles estiver perto de uma fronteira de zona.
    """
    if not anchors:
        return defaultdict(list)

    mode       = _detect_mode(anchors, img_w, img_h)
    anchor_kws = [_anchor_keywords(a["text"]) for a in anchors]
    y_zones    = _build_y_zones(anchors) if mode == "vertical" else None
    max_radius = np.linalg.norm([img_w, img_h]) * 0.55
    result     = defaultdict(list)

    # Clusteriza membros próximos espacialmente
    clusters = _cluster_members(members, max_x_gap=40, max_y_gap=30)

    for cluster_indices in clusters:
        # Centroide do cluster — representa o "componente visual" como um todo
        cx, cy = _cluster_centroid(members, cluster_indices)
        # Texto representativo do cluster (mais ao topo) para scoring semântico
        rep_idx = min(cluster_indices, key=lambda i: members[i]["center"][1])
        rep_text = " ".join(members[i]["text"] for i in cluster_indices)
        cluster_proxy = {"text": rep_text, "center": (cx, cy)}

        # ── VERTICAL: Y-zone do centroide ────────────────────────────────
        if mode == "vertical" and y_zones:
            anchor_idx = _assign_by_y_zone(cluster_proxy, y_zones)

        # ── LEGEND: semântico do texto agregado ──────────────────────────
        elif mode == "legend":
            scores = [_semantic_score(rep_text, kws) for kws in anchor_kws]
            mx = max(scores)
            if mx > 0:
                top = [i for i, s in enumerate(scores) if s == mx]
                anchor_idx = min(top,
                    key=lambda i: _distance((cx, cy), anchors[i]["center"]))
            else:
                dists = sorted((_distance((cx, cy), a["center"]), i)
                               for i, a in enumerate(anchors))
                if dists[0][0] > max_radius:
                    continue
                anchor_idx = dists[0][1]

        # ── HORIZONTAL / PROXIMITY: bounding box global + Voronoi ───────
        else:
            # 1. Calcula o bounding box de TODOS os anchors. Esta é a
            #    "região arquitetural" do diagrama. Membros fora dela
            #    (ex: User, Browser fora da caixa Web Server) são
            #    descartados — ficam sem grupo.
            arch_box = _anchors_bounding_box(anchors, img_w, img_h,
                                             margin_frac=0.05)
            if not _point_in_rect(cx, cy, arch_box):
                continue

            # 2. Dentro da região arquitetural, atribui ao anchor mais
            #    próximo (Voronoi simples).
            dists = sorted((_distance((cx, cy), a["center"]), i)
                           for i, a in enumerate(anchors))
            anchor_idx = dists[0][1]

        # Todos os membros do cluster vão para o mesmo anchor
        for i in cluster_indices:
            result[anchor_idx].append(members[i]["text"])

    return result


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------

class DiagramExtractor:

    def __init__(self, languages=None, ocr_confidence=0.30):
        self.reader   = easyocr.Reader(languages or ["pt", "en"], gpu=False)
        self.min_conf = ocr_confidence

    def extract(self, image_path: str) -> dict:
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Não foi possível abrir: {image_path}")
        h_img, w_img = img.shape[:2]

        # ── 1. OCR ──────────────────────────────────────────────────────
        raw = self.reader.readtext(img)
        raw_blocks = [
            {"text": text, "center": _bbox_center(bbox), "rect": _bbox_rect(bbox)}
            for bbox, text, prob in raw
            if prob >= self.min_conf and text.strip()
        ]

        # ── 2. Merge de fragmentos próximos ──────────────────────────────
        blocks = _merge_nearby_blocks(raw_blocks, x_gap=55, y_gap=20)

        # ── 3. text_blocks ───────────────────────────────────────────────
        text_blocks = [b["text"] for b in blocks]

        # ── 4. Classifica blocos ─────────────────────────────────────────
        anchors = []; flow_blks = []; members = []
        for b in blocks:
            if _is_skip(b["text"]):
                continue
            # Flow é verificado ANTES de anchor para evitar que textos como
            # "Database Queries" virem âncoras por conter "database".
            if _is_flow_text(b["text"]):
                flow_blks.append(b)
            elif _is_layer_anchor(b["text"]):
                anchors.append(b)
            else:
                members.append(b)

        # ── 5. Agrupamento ────────────────────────────────────────────────
        anchor_members = _group_members(anchors, members, w_img, h_img)

        # ── 6. context_groups e grouped_elements ─────────────────────────
        # Inclui anchors mesmo sem membros — eles representam containers/
        # camadas reais do diagrama (ex: "Databases" no diagrama Web Server
        # é uma caixa cilíndrica sem texto secundário interno).
        context_groups = []; grouped_elements = []
        for i, anchor in enumerate(anchors):
            mems = list(dict.fromkeys(anchor_members[i]))
            name = anchor["text"].split("\n")[0].strip()
            context_groups.append({"name": name, "contains": mems})
            grouped_elements.append({"label": name, "texts": mems})

        # ── 7. relationship_hints ─────────────────────────────────────────
        # Estratégia melhorada:
        # Setas geralmente são horizontais ou verticais. O label fica perto
        # da seta. Os endpoints corretos são os nós que estão na MESMA LINHA
        # (horizontal ou vertical) do label, não simplesmente os mais próximos.
        #
        # Algoritmo:
        #   1. Detecta orientação provável da seta a partir da forma do label
        #      (label horizontal → seta horizontal; vertical → seta vertical)
        #   2. Busca endpoints na direção de propagação da seta
        #   3. Endpoint 'from' deve estar à esquerda (ou acima) do label;
        #      'to' deve estar à direita (ou abaixo)
        relationship_hints = []; seen_rels = set()
        all_nodes  = members + anchors

        def _label_orientation(fb):
            """horizontal se rect mais largo que alto."""
            x0, y0, x1, y1 = fb["rect"]
            return "horizontal" if (x1 - x0) > (y1 - y0) else "vertical"

        for fb in flow_blks:
            orientation = _label_orientation(fb)
            fx, fy = fb["center"]
            label_w = fb["rect"][2] - fb["rect"][0]
            label_h = fb["rect"][3] - fb["rect"][1]

            if orientation == "horizontal":
                # Endpoints estão à esquerda e à direita do label.
                # Tolerância em Y: 30% da altura da imagem (cobre setas
                # longas como "xmlHttp Response" que atravessam o diagrama).
                y_tol = h_img * 0.30
                left_candidates  = [n for n in all_nodes
                                    if n["center"][0] < fx
                                    and abs(n["center"][1] - fy) < y_tol]
                right_candidates = [n for n in all_nodes
                                    if n["center"][0] > fx
                                    and abs(n["center"][1] - fy) < y_tol]
                if not left_candidates or not right_candidates:
                    continue
                # Endpoints: o mais próximo de cada lado em distância euclidiana
                src = min(left_candidates,
                          key=lambda n: _distance(n["center"], (fx, fy)))
                dst = min(right_candidates,
                          key=lambda n: _distance(n["center"], (fx, fy)))
            else:
                # Vertical: endpoints acima e abaixo do label, na mesma faixa X.
                # Tolerância em X: 30% da largura da imagem.
                x_tol = w_img * 0.30
                up_candidates   = [n for n in all_nodes
                                   if n["center"][1] < fy
                                   and abs(n["center"][0] - fx) < x_tol]
                down_candidates = [n for n in all_nodes
                                   if n["center"][1] > fy
                                   and abs(n["center"][0] - fx) < x_tol]
                if not up_candidates or not down_candidates:
                    continue
                src = min(up_candidates,
                          key=lambda n: _distance(n["center"], (fx, fy)))
                dst = min(down_candidates,
                          key=lambda n: _distance(n["center"], (fx, fy)))

            key = (src["text"], dst["text"])
            if key in seen_rels or src["text"] == dst["text"]:
                continue
            seen_rels.add(key)
            relationship_hints.append({
                "from": src["text"], "to": dst["text"], "label": fb["text"],
            })

        # ── 8. detected_keywords ─────────────────────────────────────────
        detected_keywords = []; seen_kw = set()
        for b in blocks:
            tl = b["text"].lower()
            for word, hint in KNOWLEDGE_BASE.items():
                if word in tl:
                    key = f"{b['text']}::{hint}"
                    if key not in seen_kw:
                        detected_keywords.append({"text": b["text"], "hint": hint})
                        seen_kw.add(key)

        return {
            "text_blocks":        text_blocks,
            "grouped_elements":   grouped_elements,
            "relationship_hints": relationship_hints,
            "context_groups":     context_groups,
            "detected_keywords":  detected_keywords,
        }
