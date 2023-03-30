"""Main module."""
import random
import math
import matplotlib.pyplot as plt
import numpy as np
# import mpmath as mp

POPULATION_SIZE = 200
GENERATIONS = 100
POPULATION_SAMPLE = 2
MUTATION_RANGE = 5
BYTE_LEN = 8
CHROMOSOME_LEN = 12

#             m1, m2, m3, d1, d2, d3, p1, p2, p3, q1, q2, q3
individual = [4, 8, 12, 0.65, 1.2, 1.7, 1, 0, 0, 20, 255, 10]

A = 8
B = 25
C = 4
D = 45
E = 10
F = 17
G = 35
x = np.arange(0, 100, 0.1)
original_curve = A * (B * np.sin(x / C) + D * np.cos(x / E)) + F * x - G


def get_integer(gen):
    """Returns integer value from the gen."""
    gen_val = int("".join(str(bit) for bit in gen), 2)
    # print("Valor Decimal: ", gen_val)
    return gen_val


def create_first_gen():
    """Create first generation matrix."""
    first_gen = []
    for _ in range(POPULATION_SIZE):
        chromosome = []
        for _ in range(CHROMOSOME_LEN):  # m, d, p, q * 3 == 12 numbers
            gen = [random.randint(0, 1) for _ in range(BYTE_LEN)]
            while get_integer(gen) == 0:
                gen = [random.randint(0, 1) for _ in range(BYTE_LEN)]
            chromosome.append(gen)
            # print(gen)
        first_gen.append(chromosome)
    # print(first_gen)
    return first_gen


def get_weight(chrom):
    """Returns the weight if given chromosome."""
    # print("Chromosome: ", chrom)
    biggest_number = 0
    for _, gen in enumerate(chrom):
        # print("i: ", _, "gen: ", gen)
        if get_integer(gen) > biggest_number:
            biggest_number = get_integer(gen)  # get_integer(number)
    """Probar con la división de fracciones '/' o con numero fijo"""
    weight = 255//biggest_number  # gets the integer value of the division
    # print("Peso: ", weight)
    return weight


def get_takagi_curve(chrom):
    """Returns the Takagi Sugeno curve values."""
    curve = []  # y = []
    mf1, mf2, mf3 = [], [], []
    [m_1, m_2, m_3, d_1, d_2, d_3, p_1, p_2, p_3, q_1, q_2, q_3] = chrom

    for i, number in enumerate(x):
        mf1.append(np.exp((-(number-m_1) ** 2)/(2*d_1 ** 2)))
        mf2.append(np.exp((-(number-m_2) ** 2)/(2*d_2 ** 2)))
        mf3.append(np.exp((-(number-m_3) ** 2)/(2*d_3 ** 2)))
        _b = mf1[i]+mf2[i]+mf3[i]
        a_1 = mf1[i]*(p_1*number+q_1)
        a_2 = mf2[i]*(p_2*number+q_2)
        a_3 = mf3[i]*(p_3*number+q_3)
        _a = a_1+a_2+a_3
        curve.append(_a/_b)

    # plt.ion()
    # plt.subplot(1, 2, 1)
    # plt.plot(x, mf1)
    # plt.plot(x, mf2)
    # plt.plot(x, mf3)

    # plt.subplot(1, 2, 2)
    # plt.plot(x, curve)

    # plt.show(block=False)
    # plt.pause(0.01)
    # plt.clf()
    return curve


def get_aptitude(chrom):
    """Returns the aptitude of the chromosome vs the original curve."""
    # print("Chromosome: ", chrom)

    weight = get_weight(chrom)
    # print("Peso: ", weight)
    decoded_values = []
    for _, number in enumerate(chrom):
        """Probar con la división redondeada '//'"""
        decoded_values.append(get_integer(number)/weight)
    # print("Decodificado: ", decoded_values)
    curve = get_takagi_curve(decoded_values)
    # print(curve)
    aptitude = 0
    for i in range(1000):
        diference = abs(original_curve[i] - curve[i])
        # print(diference)
        # print(original_curve[i] - curve[i])
        aptitude += diference
    # print("Aptitude: ", aptitude)
    return aptitude, curve


def tournament(population, sample_size):
    """Chooses randomly from the population a sample and returns the winner of the tournament."""
    pop_sample = random.sample(range(0, POPULATION_SIZE), sample_size)
    winner = 0
    closest_dist = math.inf
    # print(pop_sample)

    for i in range(sample_size):
        # print("Chromosome: ", population[pop_sample[i]])
        # print("Index: ", i)
        current_aptitude, curve = get_aptitude(population[pop_sample[i]])
        # print("aptitude: ", current_aptitude, "dist: ", closest_dist)
        if current_aptitude < closest_dist:
            closest_dist = current_aptitude
            winner = pop_sample[i]
    # print(pop_sample[winner])
    # print(closest_dist)
    return winner


def get_parents(population, sample_size):
    """Get the winners of the population size tournaments."""
    winners = []
    for _ in range(POPULATION_SIZE):
        winners.append(tournament(population, sample_size))
    # print(winners)
    return winners


def gen_cut(cut_index, son_part, daughter_part):
    """Gen cut method."""
    # cut_index += 1  # index goes fom 0 to 6, add 1 to center the cut for 8 bits
    X = son_part[0:cut_index]
    Y = son_part[cut_index:8]
    XX = daughter_part[0:cut_index]
    YY = daughter_part[cut_index:8]
    # print('X:', X, ' Y:', Y)
    # print('XX:', XX, ' YY:', YY)
    # print('merge_1:', X+YY)
    # print('merge_2:', XX+Y)
    return X+YY, XX+Y


def bin_array(num, size):
    """Convert a positive integer num into an m-bit bit vector"""
    return np.array(list(np.binary_repr(num).zfill(size))).astype(np.int8)


def bit_operation(part_1, part_2, operation_type):
    """Binary operation method."""
    # print("part_1: ", part_1, " part_2: ", part_2)
    result = []
    for i, num in enumerate(part_1):
        if operation_type == 1:
            result.append(num and part_2[i])
        elif operation_type == 2:
            result.append(num or part_2[i])
    # print("result: ", result)
    return result


def gen_cut_mask(cut_index, son_part, daughter_part):
    """Gen mask cut method."""
    low_mask = bin_array((2 ** cut_index)-1, BYTE_LEN)
    high_mask = bin_array(((2 ** BYTE_LEN)-1)-((2 ** cut_index)-1), BYTE_LEN)
    # print('cut_index:', cut_index)
    # print('high_mask:', high_mask,
    #      ' low_mask:', low_mask)
    # 1 == and, 2 == or
    high_part_1 = bit_operation(son_part, high_mask, 1)
    high_part_2 = bit_operation(daughter_part, high_mask, 1)
    low_part_1 = bit_operation(son_part, low_mask, 1)
    low_part_2 = bit_operation(daughter_part, low_mask, 1)

    gen_1 = bit_operation(high_part_2, low_part_1, 2)
    gen_2 = bit_operation(high_part_1, low_part_2, 2)

    # print('gen_1:', gen_1)
    # print('gen_2:', gen_2)
    return gen_1, gen_2


def mutate_if_zero(chrom):
    """Mutate a gen if is zero or by a chance."""
    result = []
    # Inverts a single bit in a gen
    if random.randint(0, 100) < MUTATION_RANGE:
        mutate = random.randint(0, 95)
        mutate_index = mutate // BYTE_LEN  # outer chromosome mutate index
        mutate_offset = mutate % BYTE_LEN  # Inner gen mutate index
        # print('mutate: ', mutate, 'mutate_index:',
        #      mutate_index, 'mutate_offset:', mutate_offset)

        chrom[mutate_index][mutate_offset] = 1 - \
            chrom[mutate_index][mutate_offset]
        # print('af: ', chrom)

    for _, gen in enumerate(chrom):
        while get_integer(gen) == 0:
            # print("Int: ", get_integer(gen), " gen: ", gen)
            gen = [random.randint(0, 1) for _ in range(BYTE_LEN)]
            # print(gen)
        result.append(gen)

    return result


def reproduction(father, mother):
    """Reproduction method."""
    # Ver si no se alteran los elementos del arreglo original de la población
    son = father.copy()
    daughter = mother.copy()

    cut = random.randint(1, 95)  # Indicates where to slice the chromosome
    cut_index = cut // BYTE_LEN  # outer chromosome cut index
    cut_index_l = math.ceil(cut / BYTE_LEN)  # outer chromosome cut index
    cut_offset = cut % BYTE_LEN  # Inner gen cut index
    # print('cut: ', cut, 'cut_index:', cut_index, ' cut_offset:', cut_offset)
    # print('father:', father, ' mother:', mother)

    X = son[0:cut_index]
    Y = son[cut_index_l:CHROMOSOME_LEN]
    XX = daughter[0:cut_index]
    YY = daughter[cut_index_l:CHROMOSOME_LEN]

    if cut_offset != 0:
        offset_1 = son[cut_index]
        offset_2 = daughter[cut_index]
        # print('X:', X, ' Y:', Y, ' offset1:', offset_1)
        # print('XX:', XX, ' YY:', YY, ' offset2:', offset_2)
        gen_1, gen_2 = gen_cut_mask(cut_offset, offset_1, offset_2)
        X.append(gen_1)
        XX.append(gen_2)
    # print('X:', X, ' Y:', Y)
    # print('XX:', XX, ' YY:', YY)
    """Deshabilite la mutación para ver si se ajusta mejor o peor"""
    son = X + YY  # mutate_if_zero(X + YY)
    daughter = XX + Y  # mutate_if_zero(XX + Y)

    # print('son:', son)
    # print('daughter:', daughter)
    return son, daughter


def get_children(population, parents):
    """Get children method."""
    # print(parents)
    children = []
    for i in range(0, POPULATION_SIZE, 2):
        son, daughter = reproduction(
            population[parents[i]], population[parents[i+1]])
        children.append(son)
        children.append(daughter)

    return children


def show_graph(curve, aptitudes):  # route, distances
    """Show Graph method."""

    plt.ion()
    plt.subplot(1, 2, 1)
    plt.plot(x, curve)
    plt.plot(x, original_curve, 'r--')
    plt.title("Best Individual Value")

    plt.subplot(1, 2, 2)
    plt.plot(aptitudes)
    plt.xlabel("Generation")
    plt.ylabel("Distance")
    plt.title("Individual Score per Generation")

    plt.suptitle("Current Aptitude: " + str(aptitudes[len(aptitudes)-1]))

    plt.subplots_adjust(left=0.1,
                        bottom=0.1,
                        right=0.9,
                        top=0.9,
                        wspace=0.4,
                        hspace=0.4)
    plt.show(block=False)
    plt.pause(0.01)
    plt.clf()


def main():
    """Main method."""
    generations_best_aptitude = []
    population = create_first_gen()

    for _ in range(GENERATIONS):
        fittest = tournament(population, POPULATION_SIZE)
        # print(fittest)
        aptitude, curve = get_aptitude(population[fittest])
        generations_best_aptitude.append(aptitude)
        # print(generations_best_aptitude)
        show_graph(curve, generations_best_aptitude)

        parents = get_parents(population, POPULATION_SAMPLE)

        children = get_children(population, parents)

        # print("Population: ", population)
        # print("Children: ", children)
        population = children
        # END FOR


main()
