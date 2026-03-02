import client from "./client";

export const uploadFile = async (file, courseId) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("course_id", courseId);

  const res = await client.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return res.data;
};