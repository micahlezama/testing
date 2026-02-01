from models import game


def card_awakened(cid):
    cm = game.Cards
    ncrd = cm.get_or_none(cm.id == cid+1)
    if ncrd:
        return cm.get_by_id(cid).name != ncrd.name 
    else:
        return True

def card_exptolv(cid, level):
    cm = game.Cards
    cem = game.CardExps

    card = cm.get_by_id(cid)
    et = card.exp_type
    tlv = card.lv_max if level == -1 else level
    tlv = card.lv_max if tlv > card.lv_max else tlv

    return int(cem.select().where(cem.lv == tlv).where(cem.exp_type == et)[0].exp_total)

def card_level(cid, exp):
    cm = game.Cards
    cem = game.CardExps

    card = cm.get_by_id(cid)
    et = card.exp_type

    return cem.select().where(cem.exp_type == et).where(cem.exp_total <= exp)[-1].lv

def card_chid(cid):
    cm = game.Cards
    return int(cm.get_by_id(cid).character_id)

def card_name(cid):
    cm = game.Cards
    return str(cm.get_by_id(cid).name)

def cards_xptolv(loci: list[int], lolv):
    """
    For each card in 'loci' return the xp needed to reach max level
    
    :param loci: list of card id 
    :type loci: list[int]
    """

    loxpmx = []
    for i, ci in enumerate(loci):
        loxpmx.append(card_exptolv(ci, lolv[i] if len(lolv) else -1))

    return loxpmx

def item_exp(tid: int):
    """
    Return exp given by the training item with id 'tid'
    
    :param tid: training item id 
    :type tid: int
    """
    return int(game.TrainingItems.get_by_id(tid).exp)
