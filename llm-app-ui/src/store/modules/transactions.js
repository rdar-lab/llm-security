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
        }
    },
    getters: {
        transactions: state => state.transactions,
    }
}