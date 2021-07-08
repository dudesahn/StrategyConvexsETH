import brownie
from brownie import Wei
from pytest import approx


def test_change_debt_with_profit(gov, token, vault, strategist, whale, strategy, curveVoterProxyStrategy):
    token.approve(vault, 2 ** 256 - 1, {"from": whale})
    vault.deposit(100e18, {"from": whale})
    strategy.harvest({"from": strategist})
    prev_params = vault.strategies(strategy).dict()

    currentDebt = vault.strategies(strategy)[2]
    vault.updateStrategyDebtRatio(strategy, currentDebt / 2, {"from": gov})
    token.transfer(strategy, Wei("100 ether"), {"from": whale})

    strategy.harvest({"from": strategist})
    new_params = vault.strategies(strategy).dict()

    assert new_params["totalGain"] > prev_params["totalGain"]
    assert new_params["totalGain"] - prev_params["totalGain"] > Wei("100 ether")
    assert new_params["debtRatio"] == currentDebt / 2
    assert new_params["totalLoss"] == prev_params["totalLoss"]
    assert approx(vault.totalAssets(), Wei("1 ether")) == strategy.estimatedTotalAssets()
