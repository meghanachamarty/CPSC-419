"""importing modularized utils_lux file to run both lux and lux_details"""
import utils_lux

def main():
    """runs lux.py"""

    filters = utils_lux.run_lux_argparse()
    query_str = """WITH Statement1 AS (
    SELECT ap.id, ap.label, COALESCE(ap.date, "") AS date, COALESCE(GROUP_CONCAT(ap.name_part, '|'), "") AS agent_info
    FROM (
        SELECT o.id, o.label, COALESCE(o.date, "") AS date, a.name || ' (' || p.part || ')' AS name_part
        FROM objects o
        LEFT JOIN productions p ON o.id = p.obj_id
        LEFT JOIN agents a ON p.agt_id = a.id
        WHERE o.label LIKE ? AND COALESCE(o.date, "") LIKE ? AND COALESCE(a.name, "") LIKE ?
        ORDER BY a.name ASC, p.part ASC
    ) ap
    GROUP BY ap.id, ap.label, ap.date
),
Statement2 AS (
    SELECT sorted_names.id, COALESCE(GROUP_CONCAT(LOWER(sorted_names.name), '|'), "") AS classifier_names
    FROM (
        SELECT o.id, LOWER(c.name) AS name
        FROM objects o
        INNER JOIN objects_classifiers j ON o.id = j.obj_id
        INNER JOIN classifiers c ON j.cls_id = c.id
        GROUP BY o.id, name
        ORDER BY name ASC
    ) sorted_names
    GROUP BY sorted_names.id
    HAVING classifier_names LIKE ?)
SELECT s1.id, s1.label, s1.date, s1.agent_info, s2.classifier_names
FROM Statement1 s1
LEFT JOIN Statement2 s2 ON s1.id = s2.id
ORDER BY s1.label, s1.date, s1.agent_info, s2.classifier_names;"""
    if filters.l is None:
        filters.l = ""
    if filters.d is None:
        filters.d = ""
    if filters.a is None:
        filters.a = ""
    if filters.c is None:
        filters.c = ""
    filters_list = [f'%{filters.l}%', f'%{filters.d}%', f'%{filters.a}%', f'%{filters.c}%']
    objects = utils_lux.connect_to_database(queries=[query_str],\
    filters=filters_list)
    print(f"Search produced {len(objects[0])} objects.")
    if len(objects[0]) > 1000:
        first_1000 = objects[0]
        first_1000 = first_1000[1:1000] # getting first 1000 items to display
        utils_lux.output_objects(first_1000, \
            ["ID", "Label", "Date", "Produced By", "Classified As"], "wwwpp")
    else:
        utils_lux.output_objects(objects[0], \
            ["ID", "Label", "Date", "Produced By", "Classified As"], "wwwpp")

if __name__ == "__main__":
    main()
