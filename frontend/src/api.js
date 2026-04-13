import axios from "axios";
// export const publicRequest = apiRequest;
import { fetchAuthSession } from "aws-amplify/auth";
import { config } from "./config";

// // ✅ API không cần auth
// export async function publicRequest(method, path, data) {
//   return axios({
//     method,
//     url: `${config.apiUrl}${path}`,
//     data,
//   });
// }

// ✅ API cần auth
// export async function apiRequest(method, path, data) {
//   try {
//     const session = await fetchAuthSession();

//     const token = session.tokens?.accessToken?.toString();

//     if (!token) {
//       throw new Error("No access token found");
//     }

//     return await axios({
//       method,
//       url: `${config.apiUrl}${path}`,
//       data,
//       headers: {
//         Authorization: `Bearer ${token}`,
//       },
//     });
//   } catch (err) {
//     console.error("API ERROR:", err);
//     throw err;
//   }
// }
export async function apiRequest(method, path, data) {
  try {
    const session = await fetchAuthSession();
    const token = session.tokens?.accessToken?.toString();

    if (!token) {
      throw new Error("No access token found");
    }

    return await axios({
      method,
      url: `${config.apiUrl}${path}`,
      data,
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  } catch (err) {
    if (err.response?.status === 401) {
      const session = await fetchAuthSession(); // refresh
      const token = session.tokens?.accessToken?.toString();

      return axios({
        method,
        url: `${config.apiUrl}${path}`,
        data,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    }

    throw err;
  }
}
// import axios from "axios";
// import { fetchAuthSession } from "aws-amplify/auth";

// const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// export async function apiRequest(method, path, data = null) {
//   const session = await fetchAuthSession();
//   const token = session.tokens?.idToken?.toString();

//   if (!token) throw new Error("No auth token found. Please login again.");

//   const url = `${API_BASE_URL}${path}`;

//   try {
//     const resp = await axios({
//       method,
//       url,
//       data,
//       headers: {
//         Authorization: `Bearer ${token}`,
//         "Content-Type": "application/json",
//       },
//     });

//     return resp.data;
//   } catch (err) {
//     console.error("API ERROR:", err);

//     const msg =
//       err?.response?.data?.error ||
//       err?.response?.data?.message ||
//       err.message ||
//       "API request failed";

//     throw new Error(msg);
//   }
// }
