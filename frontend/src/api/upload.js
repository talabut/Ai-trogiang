import api from "./client";

export function uploadFile(file, onProgress) {
  const form = new FormData();
  form.append("file", file);

  return api.post("/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: e => {
      if (onProgress) {
        onProgress(Math.round((e.loaded * 100) / e.total));
      }
    }
  });
}
