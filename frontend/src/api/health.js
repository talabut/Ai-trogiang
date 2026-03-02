import client from "./client";

export const checkHealth = async () => {
  const res = await client.get("/health");
  return res.data;
};