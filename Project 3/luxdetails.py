"""
This file takes an object id as an input, and outputs various information about that object

Author: Meghana and Ananya
"""
import utils_lux


def retrieve_object_details():
    """
    SQL command that retrieves information for the summary table.

    args: none

    returns: stmt_str (SQL string command)
    """
    stmt_str = "SELECT o.accession_no, "
    stmt_str += "ifnull(o.date, ''), GROUP_CONCAT(ifnull(p.label,'')) "
    stmt_str += "AS places, ifnull(d.name, '') "
    stmt_str += "FROM objects AS o "
    stmt_str += "LEFT JOIN objects_places AS op ON o.id = op.obj_id "
    stmt_str += "LEFT JOIN places AS p ON op.pl_id = p.id "
    stmt_str += "LEFT JOIN objects_departments AS od ON o.id = od.obj_id "
    stmt_str += "LEFT JOIN departments AS d ON od.dep_id = d.id "
    stmt_str += "WHERE o.id = ? "
    stmt_str += "GROUP BY o.accession_no, o.date, d.name"
    return stmt_str

def retrieve_label_details():
    """
    SQL command that retrieves information for the label secton.

    args: none

    returns: stmt_str (SQL string command)
    """
    stmt_str = "SELECT objects.label "
    stmt_str += "FROM objects "
    stmt_str += "WHERE objects.id = ?"
    return stmt_str

def retrieve_productions_details():
    """
    SQL command that retrieves information for the productions table.

    args: none

    returns: stmt_str (SQL string command)
    """
    stmt_str = "SELECT productions.part, agents.name, "
    stmt_str += "ifnull(nationalities.descriptor,''), "
    stmt_str += "(ifnull(strftime('%Y', agents.begin_date), '') "
    stmt_str += "|| '-' || "
    stmt_str += "ifnull(strftime('%Y', agents.end_date), '')) AS year "
    stmt_str += "FROM objects LEFT JOIN productions ON objects.id = productions.obj_id "
    stmt_str += "LEFT JOIN agents ON productions.agt_id = agents.id "
    stmt_str += "LEFT JOIN agents_nationalities ON agents.id = agents_nationalities.agt_id "
    stmt_str += "LEFT JOIN nationalities ON agents_nationalities.nat_id = nationalities.id "
    stmt_str += "WHERE objects.id = ? "
    stmt_str += "GROUP BY productions.part, agents.name, "
    stmt_str += "(agents.begin_date || '-' || agents.end_date)"
    stmt_str += "ORDER BY agents.name ASC, productions.part ASC, nationalities.descriptor ASC"
    return stmt_str

def retrieve_classifications_details():
    """
    SQL command that retrieves information for the classifications table.

    args: none

    returns: stmt_str (SQL string command)
    """
    stmt_str = "SELECT classifiers.name "
    stmt_str += "FROM classifiers "
    stmt_str += "INNER JOIN objects_classifiers "
    stmt_str += "ON objects_classifiers.cls_id = classifiers.id "
    stmt_str += "WHERE objects_classifiers.obj_id = ?"
    stmt_str += "ORDER BY classifiers.name ASC "
    return stmt_str

def retrieve_information_details():
    """
    SQL command that retrieves information for the information table.

    args: none

    returns: stmt_str (SQL string command)
    """
    stmt_str = "SELECT type, content "
    stmt_str += "FROM 'references' "
    stmt_str += "WHERE obj_id = ?"
    return stmt_str

def main(object_id):
    """
    takes in object ID and retrieves information
    """
    object_id = object_id[0]

    object_row, place_row, productions_rows, classifications_row, information_rows = utils_lux.connect_to_database(queries=[retrieve_object_details(), retrieve_label_details(), retrieve_productions_details(), retrieve_classifications_details(), retrieve_information_details()], filters=[object_id])
    summary_table = utils_lux.output_objects(list(object_row), ["Accession No.", "Date", "Place", "Department"], "pppp")
    print("summary: ", summary_table)
    label_table = utils_lux.output_objects(list(place_row), ["Label"])
    print("LABEL ", label_table)
    val = productions_rows[0]
    if val[0] is None:
        produce_table = "Produced By not found."
    else: produce_table = utils_lux.output_objects(productions_rows, ["Part", "Name", "Nationalities", "Timespan"], "pppp")
    print("PRODUCE: ", produce_table)

    class_table = utils_lux.output_objects(list(classifications_row), ["classification"])
    print("CLASS: ", class_table)

    info_table = utils_lux.output_objects(list(information_rows), ["Type", "Content"], "pp")
    print("INFO: ", info_table)

    result = f'{summary_table}\n\n{label_table}\n\n{produce_table}\n\n{class_table}\n\n{info_table}'
    return result

if __name__ == "__main__":
    main()
    """
This file takes an object id as an input, and outputs various information about that object

Author: Meghana and Ananya
"""
import utils_lux


def retrieve_object_details():
    """
    SQL command that retrieves information for the summary table.

    args: none

    returns: stmt_str (SQL string command)
    """
    stmt_str = "SELECT o.accession_no, "
    stmt_str += "ifnull(o.date, ''), GROUP_CONCAT(ifnull(p.label,'')) "
    stmt_str += "AS places, ifnull(d.name, '') "
    stmt_str += "FROM objects AS o "
    stmt_str += "LEFT JOIN objects_places AS op ON o.id = op.obj_id "
    stmt_str += "LEFT JOIN places AS p ON op.pl_id = p.id "
    stmt_str += "LEFT JOIN objects_departments AS od ON o.id = od.obj_id "
    stmt_str += "LEFT JOIN departments AS d ON od.dep_id = d.id "
    stmt_str += "WHERE o.id = ? "
    stmt_str += "GROUP BY o.accession_no, o.date, d.name"
    return stmt_str

def retrieve_label_details():
    """
    SQL command that retrieves information for the label secton.

    args: none

    returns: stmt_str (SQL string command)
    """
    stmt_str = "SELECT objects.label "
    stmt_str += "FROM objects "
    stmt_str += "WHERE objects.id = ?"
    return stmt_str

def retrieve_productions_details():
    """
    SQL command that retrieves information for the productions table.

    args: none

    returns: stmt_str (SQL string command)
    """
    stmt_str = "SELECT productions.part, agents.name, "
    stmt_str += "ifnull(nationalities.descriptor,''), "
    stmt_str += "(ifnull(strftime('%Y', agents.begin_date), '') "
    stmt_str += "|| '-' || "
    stmt_str += "ifnull(strftime('%Y', agents.end_date), '')) AS year "
    stmt_str += "FROM objects LEFT JOIN productions ON objects.id = productions.obj_id "
    stmt_str += "LEFT JOIN agents ON productions.agt_id = agents.id "
    stmt_str += "LEFT JOIN agents_nationalities ON agents.id = agents_nationalities.agt_id "
    stmt_str += "LEFT JOIN nationalities ON agents_nationalities.nat_id = nationalities.id "
    stmt_str += "WHERE objects.id = ? "
    stmt_str += "GROUP BY productions.part, agents.name, "
    stmt_str += "(agents.begin_date || '-' || agents.end_date)"
    stmt_str += "ORDER BY agents.name ASC, productions.part ASC, nationalities.descriptor ASC"
    return stmt_str

def retrieve_classifications_details():
    """
    SQL command that retrieves information for the classifications table.

    args: none

    returns: stmt_str (SQL string command)
    """
    stmt_str = "SELECT classifiers.name "
    stmt_str += "FROM classifiers "
    stmt_str += "INNER JOIN objects_classifiers "
    stmt_str += "ON objects_classifiers.cls_id = classifiers.id "
    stmt_str += "WHERE objects_classifiers.obj_id = ?"
    stmt_str += "ORDER BY classifiers.name ASC "
    return stmt_str

def retrieve_information_details():
    """
    SQL command that retrieves information for the information table.

    args: none

    returns: stmt_str (SQL string command)
    """
    stmt_str = "SELECT type, content "
    stmt_str += "FROM 'references' "
    stmt_str += "WHERE obj_id = ?"
    return stmt_str

def main(object_id):
    """
    takes in object ID and retrieves information
    """
    object_id = object_id[0]

    object_row, place_row, productions_rows, classifications_row, information_rows = utils_lux.connect_to_database(queries=[retrieve_object_details(), retrieve_label_details(), retrieve_productions_details(), retrieve_classifications_details(), retrieve_information_details()], filters=[object_id])
    summary_table = utils_lux.output_objects(list(object_row), ["Accession No.", "Date", "Place", "Department"], "pppp")
    print("summary: ", summary_table)
    label_table = utils_lux.output_objects(list(place_row), ["Label"])
    print("LABEL ", label_table)
    val = productions_rows[0]
    if val[0] is None:
        produce_table = "Produced By not found."
    else: produce_table = utils_lux.output_objects(productions_rows, ["Part", "Name", "Nationalities", "Timespan"], "pppp")
    print("PRODUCE: ", produce_table)

    class_table = utils_lux.output_objects(list(classifications_row), ["classification"])
    print("CLASS: ", class_table)

    info_table = utils_lux.output_objects(list(information_rows), ["Type", "Content"], "pp")
    print("INFO: ", info_table)

    result = f'{summary_table}\n\n{label_table}\n\n{produce_table}\n\n{class_table}\n\n{info_table}'
    return result

if __name__ == "__main__":
    main()