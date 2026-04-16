import axios from 'axios';
import type { FusedLocation } from '../types';
import { ALL_SCENARIOS } from '../mockResponse';

const API_BASE_URL = 'http://localhost:8000';

// Create a pre-configured instance for baseline configuration scaling
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Calls the locate service with the given payload.
 *
 * @param payload - The data payload required by the /locate backend endpoint.
 * @returns The FusedLocation typed response data.
 */
export const locateCaller = async (payload: any): Promise<FusedLocation> => {
  try {
    // We expect the backend to return our FusedLocation schema
    const response = await apiClient.post<FusedLocation>('/locate', payload);
    return response.data;
  } catch (error) {
    // Robust error contextualization in a production environment
    if (axios.isAxiosError(error)) {
      
      // Critical check: if there is no response, the UI tester likely doesn't have the Python backend running.
      // We will gracefully intercept the network failure and pipe in our mockResponse schemas!
      if (!error.response) {
        console.warn('Backend server offline. Injecting realistic mock scenario for UI testing...');
        await new Promise(resolve => setTimeout(resolve, 1200)); // simulate realistic fusion latency
        const randomScenario = ALL_SCENARIOS[Math.floor(Math.random() * ALL_SCENARIOS.length)];
        return randomScenario;
      }

      console.error('Locate API Error Context:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Failed to locate caller due to network error.');
    } else {
      console.error('Unexpected error during locate caller:', error);
      throw error;
    }
  }
};
