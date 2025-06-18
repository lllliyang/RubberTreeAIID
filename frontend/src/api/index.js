// src/api/index.js
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';  // 后端 API 地址

// 获取坐标信息
export const getCoordinates = async () => {
    const response = await axios.get(`${API_URL}/coordinates`);
    return response.data;
};

// 添加新的坐标信息
export const addCoordinate = async (coordinate) => {
    const response = await axios.post(`${API_URL}/coordinates`, coordinate);
    return response.data;
};