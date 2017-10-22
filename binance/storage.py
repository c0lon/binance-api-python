class Account:
    def __init__(self, raw_account):
        self.maker_commission = raw_account['makerCommission']
        self.taker_commission = raw_account['takerCommission']
        self.buyer_commission = raw_account['buyerCommission']
        self.seller_commission = raw_account['sellerCommission']

        self.can_trade = raw_account['canTrade']
        self.can_withdraw = raw_account['canWithdraw']
        self.canDeposit = raw_account['canDeposit']

        self.balances = {}
        for balance in raw_account['balances']:
            self.balances[balance['asset']] = Balance(balance)


class Balance:
    def __init__(self, raw_balance):
        self.asset = raw_balance['asset']
        self.free = float(raw_balance['free'])
        self.locked = float(raw_balance['locked'])


class Order:
    def __init__(self, raw_order):
        pass
