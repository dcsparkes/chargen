# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import argparse
import random


def dieRollN(n):
    return random.randint(1, n)


def nDn(count, size):
    rolls = []
    for i in range(count):
        roll = dieRollN(size)
        rolls.append(roll)
    return tuple(rolls)


def nD6(n):
    return nDn(n, 6)


def bestN(n, rolls):
    # print("{}: {}".format(n, rolls))
    ordered = list(reversed(sorted(rolls)))
    return ordered[:n]


def threeD6():
    return nD6(3)


def fourD6drop1():
    return bestN(3, nD6(4))


stat_names = ["STR", "INT", "WIS", "DEX", "CON", "CHA"]
statReqs = {
    "cleric": [0, 0, 9, 0, 0, 0],
    "druid": [0, 0, 12, 0, 0, 15],
    "fighter": [9, 0, 0, 0, 7, 0],
    "paladin": [12, 9, 13, 0, 9, 17],
    "ranger": [13, 13, 14, 0, 14, 0],
    "wizard": [0, 9, 0, 6, 0, 0],
    "illusionist": [0, 15, 0, 16, 0, 0],
    "thief": [0, 0, 0, 9, 0, 0],
    "assassin": [12, 11, 0, 12, 0, 0],
    "monk": [15, 0, 15, 15, 11, 0],
    "bard": [15, 12, 15, 15, 10, 15],
}


def trad():
    stats = dict()
    for name in stat_names:
        roll = threeD6()
        stats[name] = (sum(roll), roll)
    return stats


def dmgMethod1():
    stats = dict()
    for i in range(6):
        roll = nD6(4)
        total = sum(bestN(3, roll))
        stats[i] = (total, roll)
    return stats


def dmgMethod2():
    rolls = []
    for j in range(12):
        roll = nD6(3)
        total = sum(roll)
        rolls.append((total,) + roll)

    rolls.sort(reverse=True)
    stats = {}
    for i in range(6):
        stats[i] = (rolls[i][0], [rolls[i][1:], rolls[i + 6][1:]])
    return stats


def dmgMethod3():
    stats = dict()
    for name in stat_names:
        max = 0
        rolls = []
        for i in range(6):
            roll = nD6(3)
            rolls.append(roll)
            total = sum(roll)
            if total > max:
                max = total
        stats[name] = (max, rolls)
    return stats


def rollstats(method):
    funcs = [trad, dmgMethod1, dmgMethod2, dmgMethod3]
    return funcs[method]()


msgs = {
    "cleric": ["Your only career in the church is that of footstool",
               "Have you considered a career in the church?  Preach!"],
    "druid": ["Druids cannot bear you.  You are outfoxed.", "Are you neutral enough to be a Druid?  Yes, no or maybe?"],
    "fighter": ["Too feeble for fighter, Poindexter.", "You, too, can be a professional meat shield."],
    "paladin": ["Are you a paladin or a paladidn't?  The latter, sadly.",
                "Bloody [insert afterlife]!  Paladin possible."],
    "ranger": ["Ranger count irrelevant.  You are unable to range.",
               "You can be a ranger, if there are fewer than two other rangers in the room."],
    "wizard": ["You are too stupid or clumsy even to be a wizard!", "Wizard available, if you can't aim any higher."],
    "illusionist": [
        "The only illusion that you'll be weaving is that you are even remotely qualified to cast illusions.",
        "Illusionist seems to be available, or is it?"],
    "thief": ["You cannot even crime properly!", "If all else fails you can turn to a 'life' of crime."],
    "assassin": ["You overdid the hashish.  Or underdid.  Who can say?", "Assassination candidate... in both senses."],
    "monk": ["No ninjing for you.  No Monk will train you.", "You know kung fu and other monkery.  Potentially."],
    "bard": ["Not bard, moron!", "Be the best bard you can be."],
    "redshirt": ["ERROR: This should never be seen",
                 "You are a statistical outlier.  Here are your red shirt and {} hitpoints.  Good luck!"],
}


def professionsAvailable(stats):
    profs = {}
    vsActual = [stat for (stat, rolls) in stats.values()]
    # print("{}".format(vsActual))
    sortNeeded = False

    if "STR" not in stats:
        vsActual.sort()
        sortNeeded = True

    for k in statReqs.keys():
        vsRequired = statReqs[k]
        if sortNeeded:
            vsRequired.sort()
        profs[k] = False not in [(a - r) >= 0 for (a, r) in zip(vsActual, vsRequired)]
    if not [k for k in profs.keys() if profs[k] == True]:
        profs["redshirt"] = True
    return profs


def professionTestMessages(profs, quietmode):
    if not quietmode:
        yield ""

    available = [k for k in profs.keys() if profs[k] == True]
    unavailable = [k for k in profs.keys() if profs[k] == False]

    psi = None

    if "STR" in stats:
        psi, psiMsg = psionicTest(stats)
    elif max([stat for (stat, rolls) in stats.values()]) < 16:
        psi, psiMsg = psionicTest({"INT": [1], "WIS": [1], "CHA": [1]})

    if quietmode:
        if psi:
            available.append("psionicist")
        yield "AVAILABLE: " + ', '.join([p.capitalize() for p in available])
    else:
        yield "AVAILABLE"
        for p in available:
            yield " - ".join([p.capitalize(), msgs[p][1].format(dieRollN(4))])
        if psi:
            yield "Psionicist - {}".format(psiMsg)

    if quietmode:
        if psi == False:
            unavailable.append("psionicist")
        yield "UNAVAILABLE: " + ', '.join([p.capitalize() for p in unavailable])
    else:
        yield "UNAVAILABLE"
        for p in unavailable:
            yield msgs[p][0]
        if psi == False:
            yield psiMsg


def psionicTest(stats):
    success = False
    if stats["INT"][0] >= 16 or stats["WIS"][0] >= 16 or stats["CHA"][0] >= 16:
        psionicProb = 2.5 * max(0, stats["INT"][0] - 16)
        psionicProb += 1.5 * max(0, stats["WIS"][0] - 16)
        psionicProb += 0.5 * max(0, stats["CHA"][0] - 16)

        percentage = random.randint(1, 100) + int(psionicProb)  # lose the halves
        kicker = random.choice(["Womp womp", "Sad trombone", "Wilhelm scream", "Failed"])
        if percentage < 100:
            miss = 100 - percentage
            msg = "So close: {}% chance of psionics and you missed by {}%.  {}.".format(int(1 + psionicProb), miss,
                                                                                        kicker)
        else:
            success = True
            msg = "Shame your GM won't let you play a psionicist, because you rolled succesfully on a {}% chance.  {}.".format(
                percentage, kicker)
    else:
        msg = "You suck too much to be psionic."

    return (success, msg)


# def professionTestFixedStatsMessages(stats):
#     redshirt = True
#
#     if stats["WIS"][0] < 9:
#         yield ("No cleric for you! LOL!")
#     else:
#         yield ("Have you considered a career in the church beyond footstool?")
#         redshirt = False
#
#     if stats["WIS"][0] < 12 or stats["CHA"][0] < 15:
#         yield ("No druid for you! LOL!")
#     else:
#         yield ("Are you neutral enough to be a Druid?  Yes, no or maybe?  (This is a trick question)")
#         redshirt = False
#
#     if stats["STR"][0] < 9 or stats["CON"][0] < 7:
#         yield ("Too feeble for fighter, Poindexter.")
#     else:
#         yield ("Professional meat shield available.")
#         redshirt = False
#
#     if stats["STR"][0] < 12 or stats["INT"][0] < 9 or stats["WIS"][0] < 13 or stats["CON"][0] < 9 or stats["CHA"][
#         0] < 17:
#         yield ("No paladin for you! LOL!")
#     else:
#         yield ("Bloody hell!  Paladin possible.")
#         redshirt = False
#
#     if stats["STR"][0] < 13 or stats["INT"][0] < 13 or stats["WIS"][0] < 14 or stats["CON"][0] < 14:
#         yield ("Ranger count irrelevant.  You are unable to range.")
#     else:
#         yield ("You can be a ranger, if there are fewer than two other rangers in the room.")
#         redshirt = False
#
#     if stats["INT"][0] < 9 or stats["DEX"][0] < 6:
#         yield ("You are too stupid or clumsy even to be a wizard!")
#     else:
#         yield ("Wizard available, if you can't aim any higher.")
#         redshirt = False
#
#     if stats["INT"][0] < 15 or stats["DEX"][0] < 16:
#         yield ("The only weaving available to you are stories and fabric!")
#     else:
#         yield ("Illusionist seems to be available, or is that an illusion?")
#         redshirt = False
#
#     if stats["DEX"][0] < 9:
#         yield ("You cannot even crime properly!")
#     else:
#         yield ("If all else fails you can turn to a 'life' of crime.")
#         redshirt = False
#
#     if stats["STR"][0] < 12 or stats["INT"][0] < 11 or stats["DEX"][0] < 12:
#         yield ("You overdid the hashish.  Or underdid.  Who can say?")
#     else:
#         yield ("Assassination candidate... in both senses.")
#         redshirt = False
#
#     if stats["STR"][0] < 15 or stats["WIS"][0] < 15 or stats["DEX"][0] < 15 or stats["CON"][0] < 11:
#         yield ("No ninjing for you.  Monk impossible.")
#     else:
#         yield ("You know kung fu.  Monk allowed.")
#         redshirt = False
#
#     if stats["STR"][0] < 15 or stats["INT"][0] < 12 or stats["WIS"][0] < 15 or stats["DEX"][0] < 15 or stats["CON"][
#         0] < 10 or stats["CHA"][0] < 15:
#         yield ("Not bard, moron!")
#     else:
#         yield ("Be the best bard you can be.")
#         redshirt = False
#
#     if redshirt:
#         yield (
#             "You are a statistical outlier!   Here are you red shirt and {} hitpoints.  Good luck.".format(dieRollN(4)))
#
#     if stats["INT"][0] >= 16 or stats["WIS"][0] >= 16 or stats["CHA"][0] >= 16:
#         psionicProb = 1
#         psionicProb += 2.5 * max(0, stats["INT"][0] - 16)
#         psionicProb += 1.5 * max(0, stats["WIS"][0] - 16)
#         psionicProb += 0.5 * max(0, stats["CHA"][0] - 16)
#
#         percentage = int(psionicProb)  # lose the halves
#         if random.randint(1, 100) > percentage:
#             yield ("So close: {}% chance of psionics.  Failed.".format(percentage))
#         else:
#             yield (
#                 "Shame your GM won't let you play a psionicist, because you rolled succesfully on a {}% chance.  Womp womp.".format(
#                     percentage))
#
#     else:
#         yield ("You suck too much to be psionic, loser.")


def printStats(stats, quietmode):
    if not quietmode:
        for key in stats.keys():
            print("{}: {} - {}".format(key, stats[key][0], stats[key][1]))
    elif "STR" in stats:
        print(', '.join(["{}: {}".format(k, v[0]) for k, v in stats.items()]))
    else:
        print(', '.join(["{}".format(v[0]) for k, v in stats.items()]))


def professions(stats, quietmode):
    for msg in professionTestMessages(stats, quietmode):
        print(msg)


parser = argparse.ArgumentParser()
group1 = parser.add_mutually_exclusive_group()
group1.add_argument("-m", "--mode", help="Select DMG Method: 0-3 | all", choices=['0', '1', '2', '3', 'all'])
group1.add_argument("-a", "--all", help="Select all DMG Methods (equivalent to -m all)", action="store_true")
group2 = parser.add_mutually_exclusive_group()
group2.add_argument("-v", "--verbose", action="store_true", default=True)
group2.add_argument("-q", "--quiet", action="store_true")
group3 = parser.add_argument_group()
group3.add_argument("-c", "--class", help="Intended class.", choices=list(msgs.keys()))
group3.add_argument("-l", "--limit", help="Maximum number of iterations per mode to find the defined class",
                    default=100000, type=int)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    modeDescs = ["Hard mode", "DMG method 1", "DMG method 2", "DMG method 3"]

    args = parser.parse_args()
    if args.all or args.mode == "all":
        modes = range(4)
    elif args.mode is None:
        modes = [0]
    elif 0 <= int(args.mode) <= 3:
        modes = [int(args.mode)]

    c = vars(args)["class"]  # Cannot access args.class directly as class is a protected keyword
    if c is None:
        limit = 2
    else:
        limit = args.limit + 1

    for mode in modes:
        print("\n{}:".format(modeDescs[mode]))
        for i in range(1, limit):
            stats = rollstats(mode)
            profFlags = professionsAvailable(stats)
            if c and c in profFlags and profFlags[c]:
                break  # End loop: match found

        if c:
            if c in profFlags and profFlags[c]:
                print("# of iterations: {}.".format(i))
            else:
                print("No result after {} iterations.".format(i))
                continue

        printStats(stats, args.quiet)
        professions(profFlags, args.quiet)

