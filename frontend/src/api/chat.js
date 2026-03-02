import client from "./client";

export const sendMessage = async (payload) => {
  const res = await client.post("/chat", payload);
  return res.data;
};