const API_BASE_URL = 'http://127.0.0.1:8000';

/**
 * Fetches the latest grid status from the backend
 */
export async function fetchGridStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/smart-grid-status`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error("Error fetching grid status:", error);
        return null;
    }
}

/**
 * Fetches the tomorrow forecast
 */
export async function fetchTomorrowForecast() {
    try {
        const response = await fetch(`${API_BASE_URL}/forecast-tomorrow`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error("Error fetching tomorrow forecast:", error);
        return null;
    }
}

/**
 * Mocks a 24-hour solar generation curve for the chart
 * since the backend endpoint for it was disabled.
 */
export function generate24HourForecastMock(peakMW) {
    const labels = [];
    const data = [];
    
    for (let i = 0; i < 24; i++) {
        const hourLabel = `${i.toString().padStart(2, '0')}:00`;
        labels.push(hourLabel);
        
        // Simple bell curve logic peaking at 12:00
        let val = 0;
        if (i >= 6 && i <= 18) {
            // Peak at i=12
            const dist = Math.abs(12 - i);
            val = peakMW * Math.max(0, 1 - (dist / 6));
        }
        data.push(val);
    }
    
    return { labels, data };
}
