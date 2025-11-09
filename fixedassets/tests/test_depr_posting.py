import pytest
from decimal import Decimal
from finacc.models.company import Company
from finacc.models.accounts import Account
from fixedassets.models.asset import AssetCategory, Asset
from fixedassets.models.schedule import DepreciationSchedule, DepreciationLine
from fixedassets.models.config import FAAccountMapping
from fixedassets.posting.adapters import post_acquisition, post_depreciation

@pytest.mark.django_db
def test_acquire_and_depreciate_posts():
    c = Company.objects.create(name="ACME")
    asset = Account.objects.create(company=c, code="1500", name="FA Asset", kind="asset", normal_balance="debit")
    accum = Account.objects.create(company=c, code="1590", name="Accum Depr", kind="contra-asset", normal_balance="credit")
    exp = Account.objects.create(company=c, code="6100", name="Depr Expense", kind="expense", normal_balance="debit")
    gl = Account.objects.create(company=c, code="7100", name="Gain/Loss", kind="income", normal_balance="credit")
    FAAccountMapping.objects.create(company=c, asset_account=asset, accum_depr_account=accum, depr_expense_account=exp, gain_loss_account=gl)

    cat = AssetCategory.objects.create(company=c, name="Computers", depreciation_method="slm", useful_life_years=3, residual_value=0)
    a = Asset.objects.create(company=c, category=cat, code="FA-1", name="Laptop", purchase_date="2025-11-01", currency="INR", cost=Decimal("60000.00"), book_value=Decimal("60000.00"))

    from fixedassets.models.movement import Acquisition
    acq = Acquisition.objects.create(asset=a, date="2025-11-01")
    e1 = post_acquisition(acq)
    assert e1.is_posted

    sch = DepreciationSchedule.objects.create(asset=a, start_date="2025-11-30")
    dl = DepreciationLine.objects.create(schedule=sch, date="2025-11-30", amount=Decimal("1500.00"))
    e2 = post_depreciation(dl)
    assert e2.is_posted