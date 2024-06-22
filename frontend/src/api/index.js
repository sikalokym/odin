import Axios from 'axios';

let ENDPOINT = '/api';
if (process.env.NODE_ENV === 'development') {
	ENDPOINT = 'http://127.0.0.1:5000' + ENDPOINT;
} else {
	ENDPOINT = 'https://pmt-portal-backend.azurewebsites.net' + ENDPOINT;
}
const MAX_RETRIES = 2;

async function makeRequestWithRetry(call, path, data, config, retries = MAX_RETRIES) {
	try {
		return await call(ENDPOINT + path, data, config);
	} catch (error) {
		if (retries <= 0) {
			throw error;
		}
		await new Promise((resolve) => setTimeout(resolve, 500));
		return makeRequestWithRetry(call, path, data, config, retries - 1);
	}
}

export default {
	get: function (path) {
		return makeRequestWithRetry(Axios.get, path);
	},
	post: function (path, data, config) {
		return makeRequestWithRetry(Axios.post, path, data, config);
	},
	delete: function (path, options) {
		return makeRequestWithRetry(Axios.delete, path, null, options);
	},
	endpoint: ENDPOINT,
};
