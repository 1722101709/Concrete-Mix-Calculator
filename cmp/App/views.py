from django.shortcuts import render


def getSpecificGravity(grade):
    if grade == 10 or grade == 15:
        return 3.5
    if grade == 20 or grade == 25:
        return 4.0
    return 5.0


def getWaterCementRatioAndMinimumCementContent(exposure, concreteType):
    if concreteType == "Reinforced":
        if exposure == "Mild":
            return 0.55, 300
        elif exposure == "Moderate":
            return 0.50, 300
        elif exposure == "Severe":
            return 0.45, 320
        elif exposure == "Very Severe":
            return 0.45, 340
        else:
            return 0.40, 360
    else:
        if exposure == "Mild":
            return 0.60, 220
        elif exposure == "Moderate":
            return 0.60, 240
        elif exposure == "Severe":
            return 0.50, 250
        elif exposure == "Very Severe":
            return 0.45, 260
        else:
            return 0.40, 280


def getMaximumWaterContent(aggregate):
    if aggregate == "10mm":
        return 208
    if aggregate == "20mm":
        return 186
    return 165

def getVolumeOfCoarseAggregatePerUnitVolumeOfTotalAggregate(aggregate):
    if aggregate == "10mm":
        return 0.44
    if aggregate == "20mm":
        return 0.6
    return 0.69


def home(request):
    return render(request, 'home.html')


def response(request):
    if request.method == 'POST':
        grade = request.POST['grade']
        exposure = request.POST['exposure']
        concreteType = request.POST['concreteType']
        max_nom_size_agg = request.POST['max-nom-size-agg']
        meth_con_pla = request.POST['meth-con-pla']
        workability = request.POST['workability']
        sgc = float(request.POST['sgc'])
        sgca = float(request.POST['sgca'])
        sgfa = float(request.POST['sgfa'])
        sga = float(request.POST['sga'])
        item1 = [
            {'heading': 'grade', 'value': grade}, {'heading': 'exposure', 'value': exposure},
            {'heading': 'maximum nominal size aggregate', 'value': max_nom_size_agg},
            {'heading': 'method of concrete placing', 'value': meth_con_pla},
            {'heading': 'concrete type', 'value': concreteType},
            {'heading': 'workability', 'value': workability},
        ]

        item2 = [
            {'heading': 'specific gravity of cement', 'value': sgc},
            {'heading': 'specific gravity of coarse aggregate', 'value': sgca},
            {'heading': 'specific gravity of fine aggregate', 'value': sgfa},
            {'heading': 'specific gravity of water', 'value': 1},
            {'heading': 'specific gravity of admixture', 'value': sga},
        ]

        gradeNo = int(grade[1:])
        sg = getSpecificGravity(gradeNo)
        targetStrength = round(gradeNo + 1.65 * sg, 2)
        item3 = {'gradeNo': gradeNo, 'sg': sg, 'targetStrength': targetStrength}

        wcRatio, minimumCementContent = getWaterCementRatioAndMinimumCementContent(exposure, concreteType)
        adoptedWCRatio = round(wcRatio - 0.05, 2)
        item4 = {'wcRatio': wcRatio, 'adoptedWCRatio': adoptedWCRatio}

        waterContent = getMaximumWaterContent(max_nom_size_agg)
        percentage = ((int(workability[:-2]) - 50) // 25) * 3
        estimatedWater = round(waterContent * (1 + percentage / 100))
        finalWater = round(estimatedWater * 0.71)
        item5 = {'waterContent': waterContent, 'percentage': percentage,
                 'estimatedWater': estimatedWater, 'finalWater': finalWater}

        cementContent = round(finalWater / adoptedWCRatio)
        isOK = cementContent > minimumCementContent

        item6 = {'adoptedWCRatio': adoptedWCRatio, 'finalWater': finalWater, 'cementContent': cementContent,
                 'minimumCementContent': minimumCementContent, 'isOK': isOK, 'exposure': exposure}

        VolumeOfCoarseAggregate = getVolumeOfCoarseAggregatePerUnitVolumeOfTotalAggregate(max_nom_size_agg)
        isHigh = adoptedWCRatio > 0.5
        diffWCRatio = round(abs(0.5 - adoptedWCRatio), 2)
        difference = round((diffWCRatio / 0.05) * 0.01, 2)
        correctVolumeOfCoarseAggregate = round(VolumeOfCoarseAggregate + (-1 * difference if isHigh else difference), 2)
        finalVolumeOfCoarseAggregate = round(0.9 * correctVolumeOfCoarseAggregate, 2)
        finalVolumeOfFineAggregate = round(1 - finalVolumeOfCoarseAggregate, 2)

        item7 = {'max_nom_size_agg': max_nom_size_agg , 'VolumeOfCoarseAggregate': VolumeOfCoarseAggregate,
                 'isHigh': isHigh, 'adoptedWCRatio': adoptedWCRatio, 'diffWCRatio': diffWCRatio, 'difference': difference,
                 'correctVolumeOfCoarseAggregate':correctVolumeOfCoarseAggregate,
                 'finalVolumeOfCoarseAggregate': finalVolumeOfCoarseAggregate,
                 'finalVolumeOfFineAggregate': finalVolumeOfFineAggregate}

        cementVolume = round((cementContent / sgc) * (1 / 1000), 3)
        waterVolume = round((finalWater / 1) * (1 / 1000), 3)
        admixtureMass = round((2 / 100) * cementContent, 2)
        admixtureVolume = round((admixtureMass / sga) * (1 / 1000), 3)
        volumeAll = round(1 - cementVolume - waterVolume - admixtureVolume, 3)
        massOfCoarseAggregate = round(volumeAll * finalVolumeOfCoarseAggregate * sgca * 1000)
        massOfFineAggregate = round(volumeAll * finalVolumeOfFineAggregate * sgfa * 1000)

        item8 = {'cementContent': cementContent, 'cementVolume': cementVolume, 'finalWater': finalWater,
                 'waterVolume': waterVolume, 'admixtureMass': admixtureMass, 'admixtureVolume': admixtureVolume,
                 'volumeAll': volumeAll, 'finalVolumeOfCoarseAggregate': finalVolumeOfCoarseAggregate,
                 'finalVolumeOfFineAggregate': finalVolumeOfFineAggregate, 'massOfCoarseAggregate': massOfCoarseAggregate,
                 'massOfFineAggregate': massOfFineAggregate, 'sgc': sgc, 'sga': sga, 'sgca': sgca, 'sgfa': sgfa}

        ratio = "1 : " + str(round(massOfFineAggregate / cementContent, 2)) + " : " + str(round(massOfCoarseAggregate / cementContent, 2))

        item9 = {'cementContent': cementContent, 'waterContent':waterContent, 'massOfCoarseAggregate': massOfCoarseAggregate,
                 'massOfFineAggregate': massOfFineAggregate, 'admixtureMass': admixtureMass, 'adoptedWCRatio': adoptedWCRatio,
                 'ratio': ratio}

        return render(request, 'response.html', {'item1': item1, 'item2': item2,
                                                 'item3': item3, 'item4': item4, 'item5': item5,
                                                 'item6': item6, 'item7': item7, 'item8': item8, 'item9': item9})
