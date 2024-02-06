import sqlite3
from tabulate import tabulate
import telebot 
def CreateButtons():
    # Создаем соединение с базой данных
    conn = sqlite3.connect("shkaf.sqlite")
    cursor = conn.cursor()

    # Получаем все значения из указанной колонки
    cursor.execute(f"SELECT Name FROM NewTable")
    names = [row[0] for row in cursor.fetchall()]

    # Закрываем соединение с базой данных
    conn.close()
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    for name in names:
        item = telebot.types.KeyboardButton(name)
        markup.add(item)

    return markup


def ListOfItems():
    ans = ''
    try:
        connection = sqlite3.connect("shkaf.sqlite")
        cur = connection.cursor()
        cur.execute("SELECT Name, Discription, Quantity FROM NewTable")
        items = cur.fetchall()
        ans = tabulate(items, headers=['NAME', 'DISCR', 'QUANT'], tablefmt='orgtbl', colalign=('center',))
        ans = f'<pre>{ans}</pre>'
    except sqlite3.Error as e:
        print(f"Error getting list of items: {e}")
    finally:
        connection.close()
    return ans

def ListOfTaken():
    res = ''
    conn = sqlite3.connect("taken.sqlite")
    cursor = conn.cursor()

    # Получаем имена всех столбцов в таблице
    cursor.execute("PRAGMA table_info(NewTable)")
    columns = [column[1] for column in cursor.fetchall()]

    # Получаем все строки из таблицы
    cursor.execute("SELECT * FROM NewTable")
    rows = cursor.fetchall()

    # Обрабатываем каждый столбец, начиная со второго
    for i in range(1, len(columns)):
        # Собираем все ненулевые записи для текущего столбца
        non_zero_entries = [f"@{row[0]} - {row[i]}" for row in rows if row[i] != 0]

        # Если есть хотя бы одна ненулевая запись, выводим название столбца и ненулевые записи
        if non_zero_entries:
            res += f"{columns[i]} | "
            if len(non_zero_entries) > 2:
                print(f"{non_zero_entries[0]}, {non_zero_entries[1]} и еще {len(non_zero_entries) - 2}...\n")
            else:
                res += ", ".join(non_zero_entries)
                res += "\n"

    # Закрываем соединение с базой данных
    conn.close()
    return res


def ListOfTakenByName(name):
    ans = ''
    try:
        connection = sqlite3.connect("taken.sqlite")
        cur = connection.cursor()
        cur.execute(f"SELECT id, {name.upper()} FROM NewTable")
        ans = cur.fetchall()
        print(ans)
    except sqlite3.Error as e:
        print(f"Error getting list of taken items: {e}")
    finally:
        connection.close()
    temp = ['TAGS', f'{name.upper()}']
    try:
        ans1 = tabulate(ans, headers = temp,  tablefmt='orgtbl', colalign=('center',))
    except IndexError:
        return "Тег должен содержать @\n Неправильный ввод"
    ans1 = f"<pre>{ans1}</pre>"
    return ans1
def ListOfTakenByTag(name):
    try:
        with sqlite3.connect("taken.sqlite") as connection:
            cur = connection.cursor()
            cur.execute("SELECT * FROM NewTable WHERE id = ?", (name,))
            ans = cur.fetchall()
            print(ans)
    except sqlite3.Error as e:
        print(f"Error getting list of taken items: {e}")

    temp = []
    temp1 = []
    with sqlite3.connect("shkaf.sqlite") as connection:
        cur = connection.cursor()
        cur.execute("SELECT Name FROM NewTable")
        for row in cur.fetchall():
            row = str(row)
            row = row[2:-3:1]
            temp.append(row)
        print(temp, ans)
        for i in range(len(temp)):
            temp1.append([temp[i],ans[0][i+1]])
    ans = ['Items', ans[0][0]]
    ans1 = tabulate(temp1, headers=ans, tablefmt='orgtbl', colalign=('center',))
    ans1 = f"<pre>{ans1}</pre>"
    return ans1

def EditQuantity(name, q):
    try:
        connection  = sqlite3.connect("shkaf.sqlite")
        cur = connection.cursor()
        cur.execute("UPDATE NewTable SET Quantity = ? WHERE Name = ?", (q, name.upper()))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error editing quantity: {e}")
    finally:
        connection.close()

def DeleteItem(name):
    try:
        connection  = sqlite3.connect("shkaf.sqlite")
        cur = connection.cursor()
        cur.execute("DELETE FROM NewTable WHERE Name = ?", (name.upper(),))
        if cur.rowcount == 0:
            return "Неправильный ввод"
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error deleting item: {e}")
        return "Неправильный ввод"
    finally:
        connection.close()
    try:
        connection = sqlite3.connect("taken.sqlite")
        cur = connection.cursor()
        cur.execute(f"ALTER TABLE NewTable DROP COLUMN {name.upper()}")
        connection.commit()
    except sqlite3.Error as e:
        print(f'Error deleting item: {e}')
    connection.close()
    return "Успешно"


def CreateItem(name, discr, quantity):
    try:
        connection = sqlite3.connect("shkaf.sqlite")
        cur = connection.cursor()
        cur.execute("SELECT Name FROM NewTable WHERE Name=?", (name.upper(),))
        existing_item = cur.fetchone()

        if existing_item:
            ans = "Такой предмет уже есть"
        else:
            cur.execute('INSERT INTO NewTable VALUES (1, ?, ?, ?);', (name.upper(), discr, quantity))
            connection.commit()
            connection.close()

            connection = sqlite3.connect("taken.sqlite")
            cur = connection.cursor()
            cur.execute(f"ALTER TABLE NewTable ADD {name.upper()} INTEGER NOT NULL DEFAULT(0)")
            connection.commit()
            connection.close()
            ans = "Успешно выполнено"
    except sqlite3.Error as e:
        print(f"Error creating item: {e}")
        ans = "Ошибка при создании предмета"
    return ans

def TakeItemDetail(name):
    try:
        connection = sqlite3.connect("shkaf.sqlite")
        cur = connection.cursor()
        cur.execute("SELECT Name, Quantity FROM NewTable WHERE Name=?", (name.upper(),))
        item = cur.fetchone()

        if item:
            ans = f"Кол-во: {item[1]}\nСколько хотите взять?"
        else:
            ans = "Такого предмета нет"
    except sqlite3.Error as e:
        print(f"Error taking item details: {e}")
    finally:
        connection.close()
    return ans

def TakeItem(name, q, id):
    try:
        # Connect to the 'shkaf.sqlite' database
        connection = sqlite3.connect("shkaf.sqlite")
        cur = connection.cursor()

        # Retrieve the current quantity from 'NewTable'
        temp = cur.execute("SELECT Quantity FROM NewTable WHERE Name = ?", (name.upper(),)).fetchone()

        # Check if the requested quantity is more than available
        if int(q) > temp[0]:
            return "Попытка взять больше, чем имеется"

        # Update the quantity in 'NewTable'
        cur.execute("UPDATE NewTable SET Quantity = ? WHERE Name = ?", (temp[0] - int(q), name.upper()))
        connection.commit()
        connection.close()

        # Connect to the 'taken.sqlite' database
        connection = sqlite3.connect("taken.sqlite")
        cur = connection.cursor()

        # Check if the item exists for the given id in 'NewTable'
        item = cur.execute("SELECT id FROM NewTable WHERE id=?", (id,)).fetchone()


        if item:
            # Check if the specified column has a non-null value
            if cur.execute(f"SELECT {name.upper()} FROM NewTable WHERE id = ?", (id,)).fetchone()[0] is not None:
                # If the column has a value, update it by adding the requested quantity
                a = cur.execute(f"SELECT {name.upper()} FROM NewTable WHERE id = ?", (id,)).fetchone()[0]
                cur.execute("UPDATE NewTable SET {} = ? WHERE id = ?".format(name.upper()), (q + a, id))
            else:
                # If the column is null, update it with the requested quantity
                cur.execute("UPDATE NewTable SET {} = ? WHERE id = ?".format(name.upper()), (q, id))
        else:
            # If the item doesn't exist for the given id, insert a new row in 'NewTable'
            cur.execute("INSERT INTO NewTable (id, {}) VALUES (?, ?)".format(name.upper()), (id, q))

        connection.commit()
        connection.close()
    except sqlite3.Error as e:
        print(f"Error taking item: {e}")
        return "Ошибка при взятии предмета"
    return "Успешно"


def ReturnItemDetail(id):
    ans = ''
    try:
        connection = sqlite3.connect("shkaf.sqlite")
        cur = connection.cursor()
        temp = cur.execute("SELECT Name FROM NewTable").fetchall()
        print(temp)
        connection.close()

        connection  = sqlite3.connect("taken.sqlite")
        cur = connection.cursor()
        for i in temp:
            a = cur.execute(f"SELECT {i[0]} FROM NewTable WHERE id = ?", (id,)).fetchall()
            print(a)
            ans += f"{i[0]} - {str(a[0])[1:-2:1]}\n"
    except sqlite3.Error as e:
        print(f"Error returning item details: {e}")
    finally:
        connection.close()
    return ans

def ReturnItems(name, q, id):
    try:
        connection  = sqlite3.connect("taken.sqlite")
        cur = connection.cursor()
        temp = cur.execute(f"SELECT {name.upper()} FROM NewTable WHERE id = ?", (id,)).fetchone()
        if int(q) > temp[0]:
            return "Попытка вернуть больше, чем имеется"
        cur.execute(f"UPDATE NewTable SET {name.upper()} = ? WHERE id = ?", (temp[0] - int(q), id))
        connection.commit()
        connection.close()

        connection  = sqlite3.connect("shkaf.sqlite")
        cur = connection.cursor()
        temp = cur.execute("SELECT Quantity FROM NewTable WHERE Name = ?", (name.upper(),)).fetchone()
        cur.execute("UPDATE NewTable SET Quantity = ? WHERE Name = ?", (temp[0] + int(q), name.upper()))
        connection.commit()
        connection.close()
    except sqlite3.Error as e:
        print(f"Error returning item: {e}")
        return "Ошибка прям возврате предмета"
    return "Успешно"