// Author: Hassan Wahba

import Axios from 'axios';


let ENV = process.env.VUE_APP_ENV
let ENDPOINT = ""
if (process.env.NODE_ENV === 'development') {
	ENDPOINT = 'http://127.0.0.1:5000' + '/api';
} else {
	ENDPOINT = 'https://' + process.env.VUE_APP_BACKEND_HOSTNAME + '/api';
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
	env: ENV,
};
