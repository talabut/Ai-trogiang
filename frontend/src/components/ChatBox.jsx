import axios from 'axios';
import apiClient from './client';

export const sendMessage = async (courseId, question, controller) => {
  try {
    const response = await apiClient.post(
      '/api/chat',
      { course_id: courseId, question },
      { signal: controller?.signal }
    );
    return response.data;
  } catch (error) {
    if (axios.isCancel(error)) {
      throw { isCancelled: true };
    }
    throw error;
  }
};
