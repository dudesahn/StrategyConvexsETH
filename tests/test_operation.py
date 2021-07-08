import brownie
from brownie import Contract
from brownie import config

# test passes as of 21-05-20
def test_operation(gov, token, vault, dudesahn, strategist, whale, strategy, chain, strategist_ms, rewardsContract, cvx, convexWhale):
    ## deposit to the vault after approving
    startingWhale = token.balanceOf(whale)
    token.approve(vault, 2 ** 256 - 1, {"from": whale})
    vault.deposit(100e18, {"from": whale})
    newWhale = token.balanceOf(whale)
    starting_assets = vault.totalAssets()

    # harvest, store asset amount
    strategy.harvest({"from": dudesahn})
    # tx.call_trace(True)
    old_assets = vault.totalAssets()
    assert old_assets >= starting_assets

    # simulate a day of earnings
    chain.sleep(86400)
    chain.mine(1)

    # harvest after a day, store new asset amount
    tx = strategy.harvest({"from": dudesahn})
    # tx.call_trace(True)
    new_assets = vault.totalAssets()
    assert new_assets > old_assets

    # Display estimated APR based on the past month
    print("\nEstimated APR: ", "{:.2%}".format(((new_assets - old_assets) * 365) / (strategy.estimatedTotalAssets())))

    # simulate a day of earnings
    chain.sleep(86400)
    chain.mine(1)

    # test to make sure our strategy is selling convex properly. send it some from our whale.
    cvx.transfer(strategy, 1000e18, {"from": convexWhale})
    strategy.harvest({"from": dudesahn})
    new_assets_from_convex_sale = vault.totalAssets()
    assert new_assets_from_convex_sale > new_assets

    # Display estimated APR based on the past day
    print(
        "\nEstimated CVX Donation APR: ", "{:.2%}".format(((new_assets_from_convex_sale - new_assets) * 365) / (strategy.estimatedTotalAssets()))
    )

    # simulate a day of waiting for share price to bump back up
    chain.sleep(86400)
    chain.mine(1)

    # withdraw and confirm we made money
    vault.withdraw({"from": whale})
    assert token.balanceOf(whale) > startingWhale
