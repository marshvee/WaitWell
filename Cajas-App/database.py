import mysql.connector

def change_state(new_state, old_state, id_c):
    cnx = mysql.connector.connect(user='mariana', password='vulpix97',
                    host='nomasfilas2.c5h2cytdcjx1.us-west-2.rds.amazonaws.com',
                    database='mydb')
    cursor = cnx.cursor() 
    query = "UPDATE COLA SET ESTADO = %s WHERE ESTADO = %s AND CLIENTE = %s"
    data = (new_state, old_state, id_c)
    cursor.execute(query, data)
    cnx.commit() 
    cursor.close()
    cnx.close()

def get_next(caja):
    cnx = mysql.connector.connect(user='mariana', password='vulpix97',
                            host='nomasfilas2.c5h2cytdcjx1.us-west-2.rds.amazonaws.com',
                            database='mydb')
    cursor = cnx.cursor()
    query = "SELECT CLIENTE FROM COLA WHERE ESTADO = 3 AND CAJA = %s"
    cursor.execute(query, (caja,))
    retorno = cursor.fetchone()[0]
    cursor.close()
    cnx.close()
    return retorno

def next(caja):
    cnx = mysql.connector.connect(user='mariana', password='vulpix97',
                                host='nomasfilas2.c5h2cytdcjx1.us-west-2.rds.amazonaws.com',
                                database='mydb')
    cursor = cnx.cursor() 
    query = "UPDATE COLA SET ESTADO = 4 WHERE ESTADO = 3 AND CAJA = %s"
    data = (caja,)
    cursor.execute(query, data)
    cnx.commit() 
    cursor.close()

    cursor = cnx.cursor() 
    query = "UPDATE COLA SET ESTADO = 3 WHERE ESTADO = 2 AND CAJA = %s"
    data = (caja,)
    cursor.execute(query, data)
    cnx.commit() 
    cursor.close()

    cursor = cnx.cursor()
    query = "SELECT CLIENTE FROM COLA WHERE ESTADO = 1 AND CAJA = %s"
    cursor.execute(query, (caja,))
    try:
        client = cursor.fetchone()[0]
        cursor.close()
        cursor = cnx.cursor() 
        query = "UPDATE COLA SET ESTADO = 2 WHERE ESTADO = 1 AND CLIENTE = %s"
        data = (client,)
        cursor.execute(query, data)
        cnx.commit() 
        cursor.close()
    except:
        cursor.close()

    cursor = cnx.cursor()
    query = "SELECT CLIENTE FROM COLA WHERE ESTADO = 3 AND CAJA = %s"
    cursor.execute(query, (caja,))
    try:
        retorno = cursor.fetchone()[0]
    except:
        retorno = ""
    cursor.close()
    cnx.close()
    return retorno    


if __name__ == '__main__':
    # test1.py executed as script
    # do something
    print('holi')