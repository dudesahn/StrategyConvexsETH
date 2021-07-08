import brownie
from brownie import Contract
from brownie import config

# test passes as of 21-05-20
def test_simple_harvest(gov, token, vault, dudesahn, strategist, whale, strategy, chain, strategist_ms, rewardsContract):
    ## deposit to the vault after approving
    startingWhale = token.balanceOf(whale)
    token.approve(vault, 2 ** 256 - 1, {"from": whale})
    vault.deposit(100e18, {"from": whale})
    newWhale = token.balanceOf(whale)
    
    # harvest, store asset amount
    strategy.harvest({"from": gov})
    old_assets = vault.totalAssets()
    assert old_assets > 0
    assert token.balanceOf(strategy) == 0
    assert rewardsContract.balanceOf(strategy) > 0
    print("\nStaked Assets: ", rewardsContract.balanceOf(strategy)/1e18)
    print("\nStarting Assets: ", old_assets/1e18)
        
    # simulate one day of earnings
    chain.sleep(86400)
    chain.mine(1)

    # harvest after a day, store new asset amount
    print("\nClaimable CRV after 1 day: ", rewardsContract.earned(strategy)/1e18)
    strategy.harvest({"from": gov})
    print("\nClaimable CRV after 1 day and harvest: ", rewardsContract.earned(strategy)/1e18)
    # tx.call_trace(True)
    new_assets = vault.totalAssets()
    # we can't use strategyEstimated Assets because the profits are sent to the vault
    assert new_assets > old_assets
    print("\nAssets after 1 day: ", new_assets/1e18)
    print("\nStaked Assets after 1 day: ", rewardsContract.balanceOf(strategy)/1e18)


    # Display estimated APR based on the past day
    print("\nEstimated APR: ", "{:.2%}".format(((new_assets - old_assets) * 365) / (strategy.estimatedTotalAssets())))
    
    # simulate a day of waiting for share price to bump back up
    chain.sleep(86400)
    chain.mine(1)
    
    # withdraw and confirm we made money
    vault.withdraw({"from": whale})    
    assert token.balanceOf(whale) > startingWhale 