import datetime
import webbrowser
import os

kayak_template = r"http://www.kayak.com/flights/{}-{}/{}/{}"
kayak_template_one_way = r"http://www.kayak.com/flights/{}-{}/{}"

path = os.path.dirname(__file__)

def update_db():
    f = open(os.path.join(path, "db.txt"), "r+")
    pos = f.tell()
    new_number = int(f.readline()) + 1

    f.seek(pos)
    f.write(str(new_number))

def iterate_over_flights(flights_data, from_number=0):
    print "start from", from_number
    for flight in flights_data[from_number:]:
        raw_input("Press Enter for next flight")

        conn_type = flight[-1]
        source = flight[3][0]
        dst = flight[3][1]
        depart_from_src_date = flight[3][2]
        depart_from_dst_date = flight[3][3]

        roundtrip_url = kayak_template.format(source, dst, depart_from_src_date,
                                              depart_from_dst_date)
        webbrowser.open(roundtrip_url)
        print flight
        if conn_type.startswith("Two Connections"):
            conn = conn_type.split(" ")[7]
            conn_date = conn_type.split(" ")[9]

            if "beginning" in conn_type:
                conn_url1 = kayak_template.format(source, conn, depart_from_src_date,
                                              depart_from_dst_date)

                conn_url2 = kayak_template.format(conn, dst, conn_date,
                                              depart_from_dst_date)

                webbrowser.open(conn_url1)
                webbrowser.open(conn_url2)
            elif "end" in conn_type:
                conn_url1 = kayak_template.format(source, conn, depart_from_src_date,
                                              depart_from_dst_date)

                conn_url2 = kayak_template.format(conn, dst, depart_from_src_date,
                                              conn_date)

                webbrowser.open(conn_url1)
                webbrowser.open(conn_url2)


        elif conn_type == 'Two one ways':
            conn_url1 = kayak_template_one_way.format(source, dst, depart_from_src_date)

            conn_url2 = kayak_template_one_way.format(dst, source, depart_from_dst_date)

            webbrowser.open(conn_url1)
            webbrowser.open(conn_url2)

        elif conn_type.startswith("Connection in"):
            conn = conn_type.split(" ")[4]
            conn_date = conn_type.split(" ")[6]

            if "end" in conn_type:
                conn_url1 = kayak_template_one_way.format(source, dst, depart_from_src_date)

                conn_url2 = kayak_template_one_way.format(dst, conn, conn_date)

                conn_url3 = kayak_template_one_way.format(conn, source, depart_from_dst_date)

                webbrowser.open(conn_url1)
                webbrowser.open(conn_url2)
                webbrowser.open(conn_url3)

            elif "beginning" in conn_type:
                conn_url1 = kayak_template_one_way.format(source, conn, depart_from_src_date)

                conn_url2 = kayak_template_one_way.format(conn, dst, conn_date)

                conn_url3 = kayak_template_one_way.format(dst, source, depart_from_dst_date)

                webbrowser.open(conn_url1)
                webbrowser.open(conn_url2)
                webbrowser.open(conn_url3)

        else:

            raise Exception("Unknown flight type")

        update_db()
        

if __name__ == "__main__":
    f = open(os.path.join(path,"flights_data.txt"))
    lines = f.readlines()
    flights_data = eval("".join(lines))
    f.close()

    f = open(os.path.join(path,"db.txt"))
    flight_number = int(f.readline())
    f.close()
    iterate_over_flights(flights_data, flight_number)
