MIXSTRING = "0.0000000000 H 0.9997000000 He 0.0000000000 Li 0.0000000000 Be 0.0000000000 B 0.0000511731 C 0.0000149947 N 0.0001391936 O 0.0000000089 F 0.0000312191 Ne 0.0000006325 Na 0.0000118928 Mg 0.0000010246 Al 0.0000128248 Si 0.0000001123 P 0.0000088226 S 0.0000001442 Cl 0.0000012913 Ar 0.0000000663 K 0.0000011815 Ca 0.0000000009 Sc 0.0000000645 Ti 0.0000000066 V 0.0000003130 Cr 0.0000001735 Mn 0.0000227260 Fe 0.0000000631 Co 0.0000013430 Ni 0.0000000133 Cu 0.0000000335 Zn"
MIXNAME = "X0 Y999 Z0"
MASSFRAC = False

def test_valid_connection():

    from pyTOPSScrape.api.api import submit_TOPS_form

    tableHTML = submit_TOPS_form(MIXSTRING, MIXNAME, MASSFRAC)

    with open("./tableHTMLRaw.html", 'rb') as target:
        assert tableHTML == target.read()


def test_TOPS_table_parse():
    from pyTOPSScrape.api.api import parse_table

    with open("./tableHTMLRaw.html", "rb") as f:
        tableHTML = f.read()

    table = parse_table(tableHTML)

    with open("./targetParsedTable.dat", 'r') as f:
        target = f.read()

    assert table == target


def generate_comparison_file():
    from pyTOPSScrape.api.api import submit_TOPS_form

    print("Getting comparison file")
    tableHTML = submit_TOPS_form(MIXSTRING, MIXNAME, MASSFRAC)

    with open("./tableHTMLRaw.html", 'wb') as out:
        print("Writing")
        out.write(tableHTML)

def generate_parsed_table():
    from pyTOPSScrape.api.api import parse_table

    with open("./tableHTMLRaw.html", "rb") as f:
        tableHTML = f.read()

    print("Parsing targe raw HTML table")
    table = parse_table(tableHTML)

    with open("./targetParsedTable.dat", 'w') as f:
        print("Writing")
        f.write(table)


if __name__ == "__main__":
    generate_comparison_file()
    generate_parsed_table()



