import { createStore } from 'vuex'
import auth from './modules/auth'
import transactions from './modules/transactions'

const store = createStore({
    modules: {
        auth,
        transactions
    }
})

export default store