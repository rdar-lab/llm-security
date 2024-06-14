export default {
    namespaced: true,
    state: {
        username: null,
        password: null,
        authenticated: false,
    },
    mutations: {
        saveCredentials(state, { username, password }) {
            state.username = username;
            state.password = password;
            state.authenticated = true;
        },
        logout(state) {
            state.username = null;
            state.password = null;
            state.authenticated = false;
        }
    },
    actions: {
        login({ commit }, { username, password }) {
            return new Promise((resolve, reject) => {
                fetch('/api/ping/', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Basic ' + btoa(username + ":" + password)
                    },
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response;
                    })
                    .then(response => {
                        alert(response.status);
                        commit('saveCredentials', { username, password });
                        resolve(response);
                    })
                    .catch(error => {
                        reject(error);
                    });
            });
        }
    },
    getters: {
        isAuthenticated: state => state.authenticated,
    }
}