import Axios from 'axios';

let ENDPOINT = '/api';
if (process.env.NODE_ENV === 'development') {
	ENDPOINT = 'https://pmt-portal-backend.azurewebsites.net' + ENDPOINT;
}

export default {
	get: function (path) {
		return Axios.get(ENDPOINT + path);
	},
	post: function (path, data, config) {
		return Axios.post(ENDPOINT + path, data, config);
	},
	delete: function (path, options) {
		return Axios.delete(ENDPOINT + path, options);
	},
};
