import streamlit as st
import numpy as np
import pandas as pd
import networkx as nx
from pyvis.network import Network
import tempfile
import os

st.set_page_config(page_title="Алгоритм Мальгранжа для разбиения графа на сильно связные подграфы.", layout="wide")
st.title("Алгоритм Мальгранжа для разбиения графа на сильно связные подграфы.")

st.markdown("""
#### 1. Выберите размерность матрицы (n x n)
#### 2. Кликните по клетке (чекбоксу), чтобы добавить/убрать связь (1/0)
""")

def get_default_matrix(n):
    arr = np.zeros((n, n), dtype=int)
    if n == 10:
        arr[0, 9] = 1  
        arr[1, 0] = 1
        arr[1, 3] = 1
        arr[2, 1] = 1
        arr[2, 4] = 1     
        arr[3, 4] = 1  
        arr[4, 3] = 1  
        arr[5, 2] = 1  
        arr[6, 4] = 1
        arr[6, 7] = 1  
        arr[7, 8] = 1  
        arr[8, 6] = 1
        arr[8, 9] = 1   
        arr[9, 2] = 1
        arr[9,5] = 1
    return arr

def get_matrix_from_checkboxes(n):
    cols = [f"x{i+1}" for i in range(n)]
    if 'matrix_init' not in st.session_state or st.session_state['matrix_init'] != n:
        # Инициализация дефолтной матрицы
        arr = get_default_matrix(n)
        st.session_state['matrix'] = arr.tolist()
        st.session_state['matrix_init'] = n
    arr = np.array(st.session_state['matrix'])
    st.markdown("##### Матрица смежности (отметьте связи):")
    table = []
    for i in range(n):
        row = []
        cols_row = st.columns(n+1, gap="small")
        cols_row[0].markdown(f"**{cols[i]}**")
        for j in range(n):
            key = f"cell_{i}_{j}"
            val = cols_row[j+1].checkbox("", value=bool(arr[i, j]), key=key)
            arr[i, j] = 1 if val else 0
            row.append(val)
        table.append(row)
    # подписи столбцов сверху
    cols_header = st.columns(n+1, gap="small")
    cols_header[0].markdown("")
    for j in range(n):
        cols_header[j+1].markdown(f"**{cols[j]}**")
    # Сохраняем текущее состояние
    st.session_state['matrix'] = arr.tolist()
    return arr, cols

def malgrange_stepwise(adj, cols):
    n = adj.shape[0]
    remaining = set(range(n))
    steps = []
    adj_work = adj.copy()
    while remaining:
        v = min(remaining)  # минимальный по номеру узел
        # Прямое замыкание для v
        direct = np.zeros(n, dtype=int)
        stack = [v]
        visited = set()
        while stack:
            node = stack.pop()
            if node in visited or node not in remaining:
                continue
            visited.add(node)
            direct[node] = 1
            for j in range(n):
                if adj_work[node, j] and j in remaining:
                    stack.append(j)
        # Обратное замыкание для v
        inverse = np.zeros(n, dtype=int)
        stack = [v]
        visited = set()
        while stack:
            node = stack.pop()
            if node in visited or node not in remaining:
                continue
            visited.add(node)
            inverse[node] = 1
            for i in range(n):
                if adj_work[i, node] and i in remaining:
                    stack.append(i)
        # Пересечение
        intersection = (direct & inverse)
        # Узлы, которые будут удалены на этом шаге
        to_remove = {idx for idx in range(n) if intersection[idx]}
        # Оставшиеся после удаления
        next_remaining = remaining - to_remove
        steps.append({
            "chosen": v,
            "direct": direct.copy(),
            "inverse": inverse.copy(),
            "intersection": intersection.copy(),
            "remaining": set(next_remaining),
            "removed": to_remove
        })
        # Удалить все узлы из пересечения
        remaining = next_remaining
    return steps

def show_stepwise_closures(steps, cols):
    for i, s in enumerate(steps):
        chosen = s['chosen']
        st.markdown(f"### Шаг {i+1}")
        st.markdown(f"**Выбран узел:** {cols[chosen]}")
        direct_set = {cols[j] for j in range(len(cols)) if s['direct'][j]}
        inverse_set = {cols[j] for j in range(len(cols)) if s['inverse'][j]}
        inter_set = {cols[j] for j in range(len(cols)) if s['intersection'][j]}
        removed_set = {cols[j] for j in s['removed']}
        st.markdown(f"- Г{cols[chosen]} = {{{', '.join(sorted(direct_set))}}}")
        st.markdown(f"- Г⁻¹{cols[chosen]} = {{{', '.join(sorted(inverse_set))}}}")
        st.markdown(f"- Г{cols[chosen]} ∩ Г⁻¹{cols[chosen]} = {{{', '.join(sorted(inter_set))}}}")
        st.markdown(f"**Удалены на этом шаге:** {', '.join(sorted(removed_set)) if removed_set else 'нет'}")
        st.markdown(f"**Оставшиеся узлы:** {', '.join([cols[x] for x in sorted(s['remaining'])]) if s['remaining'] else 'нет'}")
        st.markdown("---")

def draw_clusters(adj, intersection, cols):
    n = adj.shape[0]
    G_inter = nx.from_numpy_array(intersection)
    clusters = list(nx.connected_components(G_inter.to_undirected()))
    cluster_map = {}
    for idx, nodes in enumerate(clusters):
        for node in nodes:
            cluster_map[node] = idx
    net = Network(height="400px", width="100%", directed=True, notebook=False)
    colors = ["#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", "#46f0f0", "#f032e6"]
    for node in range(n):
        group = cluster_map.get(node, -1)
        color = colors[group % len(colors)] if group >= 0 else "#cccccc"
        net.add_node(node, label=cols[node], color=color, size=12)
    for i in range(n):
        for j in range(n):
            if adj[i, j]:
                net.add_edge(i, j)
    with tempfile.TemporaryDirectory() as tmpdirname:
        html_path = os.path.join(tmpdirname, "graph.html")
        net.save_graph(html_path)
        st.components.v1.html(open(html_path, 'r', encoding='utf-8').read(), height=420, scrolling=True)

def main():
    n = st.number_input("Размерность n:", min_value=2, max_value=12, value=10, step=1)
    adj, cols = get_matrix_from_checkboxes(n)
    st.write(f"Размер матрицы: {adj.shape[0]}x{adj.shape[1]}")
    if st.button("Запустить алгоритм Мальгранжа"):
        steps = malgrange_stepwise(adj, cols)
        st.subheader("Пошаговое выполнение алгоритма Мальгранжа:")
        show_stepwise_closures(steps, cols)
        st.subheader("Визуализация итогового графа с кластерами:")
        # Для визуализации используем финальное пересечение (итоговые кластеры)
        final_intersection = np.zeros_like(adj)
        for s in steps:
            # Для каждого шага добавим рёбра между всеми в пересечении
            idxs = [i for i, v in enumerate(s['intersection']) if v]
            for i in idxs:
                for j in idxs:
                    final_intersection[i, j] = 1
        draw_clusters(adj, final_intersection, cols)

if __name__ == "__main__":
    main()
