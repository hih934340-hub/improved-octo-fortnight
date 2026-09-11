const express = require('express');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3391;

// Cấu hình API gốc
const API_TAIXIU_MD5 = "https://luck8bot.com/api/GetNewLottery/TaixiuMd5";
const API_SICBO40 = "https://luck8bot.com/api/GetNewLottery/Sicbo40";

async function fetchLotteryData(apiUrl) {
    try {
        const response = await axios.get(apiUrl, { timeout: 10000 });
        return response.data;
    } catch (error) {
        return { state: 0, error: error.message };
    }
}

function processResponse(data) {
    if (data.state !== 1 || !data.data) {
        return null;
    }
    
    const lotteryData = data.data;
    const openCode = lotteryData.OpenCode || "";
    
    // Tách các xúc xắc
    let xucXacList = openCode.split(",");
    while (xucXacList.length < 3) {
        xucXacList.push("0");
    }
    
    const xucXac1 = parseInt(xucXacList[0], 10);
    const xucXac2 = parseInt(xucXacList[1], 10);
    const xucXac3 = parseInt(xucXacList[2], 10);
    
    // Tính tổng
    const tong = xucXac1 + xucXac2 + xucXac3;
    
    // Xác định kết quả (Tài/Xỉu)
    let ketQua = "Không xác định";
    if (11 <= tong && tong <= 17) {
        ketQua = "Tài";
    } else if (4 <= tong && tong <= 10) {
        ketQua = "Xỉu";
    }
    
    const now = new Date();
    const updateAt = lotteryData.OpenTime || now.toISOString().slice(0, 19).replace('T', ' ');

    return {
        phien: lotteryData.Expect || "",
        xuc_xac_1: xucXac1,
        xuc_xac_2: xucXac2,
        xuc_xac_3: xucXac3,
        tong: tong,
        ket_qua: ketQua,
        update_at: updateAt
    };
}

app.get('/api/txmd5', async (req, res) => {
    const rawData = await fetchLotteryData(API_TAIXIU_MD5);
    const result = processResponse(rawData);
    
    if (result) {
        res.json(result);
    } else {
        res.status(500).json({ error: "Không thể lấy dữ liệu từ API gốc" });
    }
});

app.get('/api/sicbo40', async (req, res) => {
    const rawData = await fetchLotteryData(API_SICBO40);
    const result = processResponse(rawData);
    
    if (result) {
        res.json(result);
    } else {
        res.status(500).json({ error: "Không thể lấy dữ liệu từ API gốc" });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on port ${PORT}`);
});
