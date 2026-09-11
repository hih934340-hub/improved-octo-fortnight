from flask import Flask, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Cấu hình API gốc
API_TAIXIU_MD5 = "https://luck8bot.com/api/GetNewLottery/TaixiuMd5"
API_SICBO40 = "https://luck8bot.com/api/GetNewLottery/Sicbo40"

def fetch_lottery_data(api_url):
    """Lấy dữ liệu từ API gốc"""
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"state": 0, "error": str(e)}

def process_response(data, table_name):
    """Xử lý và format dữ liệu response"""
    if data.get("state") != 1 or not data.get("data"):
        return None
    
    lottery_data = data["data"]
    open_code = lottery_data.get("OpenCode", "")
    
    # Tách các xúc xắc
    xuc_xac_list = open_code.split(",")
    
    # Đảm bảo có đủ 3 xúc xắc
    while len(xuc_xac_list) < 3:
        xuc_xac_list.append("0")
    
    xuc_xac_1 = int(xuc_xac_list[0])
    xuc_xac_2 = int(xuc_xac_list[1])
    xuc_xac_3 = int(xuc_xac_list[2])
    
    # Tính tổng
    tong = xuc_xac_1 + xuc_xac_2 + xuc_xac_3
    
    # Xác định kết quả (Tài/Xỉu)
    # Tài: tổng từ 11-17, Xỉu: tổng từ 4-10
    if 11 <= tong <= 17:
        ket_qua = "Tài"
    elif 4 <= tong <= 10:
        ket_qua = "Xỉu"
    else:
        ket_qua = "Không xác định"
    
    # Format response
    result = {
        "phien": lottery_data.get("Expect", ""),
        "xuc_xac_1": xuc_xac_1,
        "xuc_xac_2": xuc_xac_2,
        "xuc_xac_3": xuc_xac_3,
        "tong": tong,
        "ket_qua": ket_qua,
        "update_at": lottery_data.get("OpenTime", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    }
    
    return result

@app.route('/api/txmd5', methods=['GET'])
def get_taixiu_md5():
    """Endpoint cho Tài Xỉu MD5"""
    raw_data = fetch_lottery_data(API_TAIXIU_MD5)
    result = process_response(raw_data, "TaixiuMD5")
    
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Không thể lấy dữ liệu từ API gốc"}), 500

@app.route('/api/sicbo40', methods=['GET'])
def get_sicbo40():
    """Endpoint cho Sicbo40"""
    raw_data = fetch_lottery_data(API_SICBO40)
    result = process_response(raw_data, "Sicbo40")
    
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Không thể lấy dữ liệu từ API gốc"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3391, debug=True)
