export default {
    namespaced: true,
    state: {
        transactions: null,
    },
    mutations: {
        setTransactions(state, { transactions }) {
            state.transactions = transactions;
        },
    },
    actions: {
        refreshTransactions({ commit, rootState }) {
            const { username, password } = rootState.auth;
            const encodedCredentials = btoa(`${username}:${password}`);
            return new Promise((resolve, reject) => {
                fetch('/api/transaction_manager/transaction/', {
                    headers: {
                        'Authorization': `Basic ${encodedCredentials}`
                    }
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        commit('setTransactions', { transactions: data });
                        resolve();
                    })
                    .catch(error => {
                        reject(error);
                    });
            });
        },
        addTransaction({ dispatch, rootState }, { transaction }) {
            const { username, password } = rootState.auth;
            const encodedCredentials = btoa(`${username}:${password}`);
            return new Promise((resolve, reject) => {
                fetch('/api/transaction_manager/transaction/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Basic ${encodedCredentials}`
                    },
                    body: JSON.stringify(transaction)
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response;
                    })
                    .then(() => {
                        dispatch('refreshTransactions');
                        resolve();
                    })
                    .catch(error => {
                        reject(error);
                    });
            });
        },
        askQuestion({ dispatch, rootState }, { mode, query }) {
            const { username, password } = rootState.auth;
            const {selectedProtector} = rootState.protections;
            const encodedCredentials = btoa(`${username}:${password}`);
            return new Promise((resolve, reject) => {
                let url = null;
                if (mode === "rag") {
                    url = '/api/transaction_manager/ask-rag/';
                } else if (mode === "preloaded") {
                    url = '/api/transaction_manager/ask-preloaded/';
                } else if (mode === "sql") {
                    url = '/api/transaction_manager/ask-sql/';
                } else {
                    reject(new Error(`Invalid mode: ${mode}`));
                    return;
                }

                url += '?query=' + encodeURIComponent(query);

                if (selectedProtector !== 'none') {
                    url += '&protector=' + selectedProtector;
                }

                fetch(url, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Basic ${encodedCredentials}`
                    }
                })
                    .then(async response => {
                        if (!response.ok) {
                            let errorMsg = await response.text();
                            if (!errorMsg) {
                                errorMsg = `HTTP error! status: ${response.status}`
                            }
                            throw new Error(errorMsg);
                        }
                        return response;
                    })
                    .then((response) => {
                        resolve(response);
                    })
                    .catch(error => {
                        reject(error);
                    });
            });
        }
    },
    getters: {
        transactions: state => state.transactions,
    }
}