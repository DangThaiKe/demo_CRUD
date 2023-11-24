from flask import Flask, render_template, request,jsonify, send_file
import mysql.connector
from openpyxl import Workbook
from io import BytesIO
app = Flask(__name__)

#Connect DB
conn = mysql.connector.connect(
    host = "127.0.0.1",
    user = "root",
    password = "123456",
    database = "demoPython",
    #connect_timeout=6000  # Giả sử timeout là 30 giây, bạn có thể list chỉnh giá trị này
)
#Tạo đối tượng cursor
#cursor = conn.cursor()

#Hiển thị dữ liệu
@app.route('/')
def show_data():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM BảngCông")
    data = cursor.fetchall()
    return render_template('index.html', data=data)
#Create Data
@app.route('/create', methods=['POST'])
def create_data():
# Lấy dữ liệu từ request form
    maNV = request.form['MãNV']
    tenNV = request.form['TênNV']
    ngay = request.form['Ngày']
    gioVao = request.form['GiờVào']
    gioRa = request.form['GiờRa']
    ghiChu = request.form['GhiChú']
# Thực hiện câu lệnh INSERT vào cơ sở dữ liệu
    cursor = conn.cursor()
    cursor.execute("INSERT INTO BảngCông (MaNV, TenNV, Ngay, GioVao, GioRa, GhiChu) VALUES (%s, %s, %s, %s, %s, %s)", (maNV,tenNV,ngay,gioVao,gioRa,ghiChu))
    conn.commit()
# Lấy dữ liệu mới từ cơ sở dữ liệu
    cursor.execute("SELECT * FROM BảngCông")
    new_data = cursor.fetchall()
    return render_template('index.html', data = new_data)
#Update Data
@app.route('/update', methods=['POST'])
def update_data():
    # Lấy dữ liệu từ request form
    tenNV = request.form['TênNV']
    ngay = request.form['Ngày']
    gioVao = request.form['GiờVào']
    gioRa = request.form['GiờRa']
    ghiChu = request.form['GhiChú']
    data_id = request.form['MãNV']
# Thực hiện câu lệnh UPDATE trong cơ sở dữ liệu
    cursor = conn.cursor()
    cursor.execute("UPDATE BảngCông SET TenNV = %s, Ngay = %s, GioVao = %s, GioRa = %s, GhiChu = %s WHERE MaNV = %s AND Ngay = %s", (tenNV,ngay,gioVao,gioRa,ghiChu,data_id,ngay))
    conn.commit()
# Lấy dữ liệu mới từ cơ sở dữ liệu
    cursor.execute("SELECT * FROM BảngCông")
    new_data = cursor.fetchall()
    return render_template('index.html', data = new_data)

#Delete Data
@app.route('/delete', methods=['POST'])
def delete_data():
# Lấy dữ liệu từ request form
    data_id = request.form['MãNV']
    ngay = request.form['Ngay']
# Thực hiện câu lệnh DELETE trong cơ sở dữ liệu
    cursor = conn.cursor()
    cursor.execute("DELETE FROM BảngCông WHERE MaNV = %s AND Ngay = %s", (data_id,ngay))
    conn.commit()
# Lấy dữ liệu mới từ cơ sở dữ liệu
    cursor.execute("SELECT * FROM BảngCông")
    new_data = cursor.fetchall()
    return render_template('index.html', data =new_data)

#Tính số ngày làm việc
@app.route('/so_ngay_lam_viec', methods=['POST'])
def so_ngay_lam_viec():
    cursor = conn.cursor()
    if request.method == 'POST':
        maNV = request.form['MãNV']
        ngayLamViec = count_NgayLamViec()
        # Lấy dữ liệu mới từ cơ sở dữ liệu
        cursor.execute("SELECT * FROM BảngCông")
        new_data = cursor.fetchall()
        return render_template('index.html', maNV=maNV, ngayLamViec=ngayLamViec, data=new_data)
def count_NgayLamViec():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MaNV, COUNT(Ngay) AS SoNgayLamViec FROM BảngCông GROUP BY MaNV;")
        rs = cursor.fetchall()

        if rs:
            return rs
        else:
            return "Không có thông tin ngày làm việc cho nhân viên này"
    except Exception as e:
        return f"Lỗi: {str(e)}"
    finally:

        cursor.close()

    # rs_text = ""
    # for result in rs:
    #     ma = result[0]
    #     soNgayLamViec = result[1]
    #     rs_text += f"Mã Nhân Viên: {ma}, Số Ngày Làm Việc: {soNgayLamViec}\n"
    #
    # return rs_text
#Xuất file excel dựa vào mã NV
@app.route('/down', methods = ['POST'])
def export_Excel():
    maNV = request.form['maNV']
    cursor = conn.cursor()
    query = f"SELECT * FROM BảngCông WHERE MaNV = '{maNV}'"
    cursor.execute(query)
    data = cursor.fetchall()
#Tạo file
    wb = Workbook()
    ws = wb.active
#GHi dữ liệu từ câu truy vấn vào file excel
    ws.append(cursor.column_names)

    for row in data:
        ws.append(row)

    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
#Gửi file về để tải
    return send_file(excel_file, download_name='data.xlsx', as_attachment=True)
#Lọc NV
@app.route('/search', methods=['POST'])
def filter_nhanVien():
    maNV = request.form['maNV']
    cursor = conn.cursor()
    query = f"SELECT * FROM BảngCông WHERE MaNV = '{maNV}'"
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template('index.html', data=data)
if __name__ == '__main__':
    app.run(debug=True)
