"""importing modularized utils_lux file to run both lux and lux_details"""
import utils_lux

def main(filters_list):
    """
    runs lux.py
    """
    query_str = """with my_agents AS (SELECT ap.id, ap.label AS label,
     COALESCE(ap.date, "") AS date, COALESCE(GROUP_CONCAT(ap.name_part, '|'), "") AS agent_info
    FROM (
    SELECT o.id, o.label, COALESCE(o.date, "") AS date, a.name || ' (' || p.part || ')' AS name_part
    FROM objects o
    LEFT JOIN productions p ON o.id = p.obj_id
    LEFT JOIN agents a ON p.agt_id = a.id
    ORDER BY a.name ASC, p.part ASC
    ) ap
    GROUP BY ap.id, ap.label, ap.date
    ), my_classifiers as (
    SELECT sorted_names.id, COALESCE(GROUP_CONCAT(LOWER(sorted_names.name), '|'), "") AS classifier_names
    FROM (
        SELECT o.id, LOWER(c.name) AS name
        FROM objects o
        LEFT OUTER JOIN objects_classifiers j ON o.id = j.obj_id
        LEFT OUTER JOIN classifiers c ON j.cls_id = c.id
        GROUP BY o.id, name
        ORDER BY name ASC
    ) sorted_names
    GROUP BY sorted_names.id
    HAVING classifier_names LIKE ?
    )
    select s1.id, s1.label, s1.date, s1.agent_info, COALESCE(s2.classifier_names, "")
    from my_agents s1
    INNER JOIN my_classifiers s2 ON s1.id = s2.id
    WHERE 1 = 1"""

    filters_list[0] = f"%{filters_list[0]}%"
    query_str += """ AND INSTR(lower(s1.date), LOWER(?))"""
    query_str += """ AND INSTR(LOWER(COALESCE(s1.agent_info, '')), LOWER(?))"""
    query_str += """ AND INSTR(lower(s1.label), LOWER(?))"""
    query_str += """ ORDER BY s1.label, s1.date, s1.agent_info, s2.classifier_names DESC LIMIT 1000"""

    objects = utils_lux.connect_to_database(queries=[query_str],\
    filters=filters_list)

    results = utils_lux.output_objects(objects[0], ["", "", "", "", ""], "wwwpp")
    # print(filters_list)
    return results

if __name__ == "__main__":
    main()