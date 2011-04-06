# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: meego-qa@lists.meego.com
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# version 2.1 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA
# ***** END LICENCE BLOCK *****

""" Schedule algorithm """

def group_packages(packages, max_runtime=60, max_groups=1000):
    """
    @type packages: C{dict} of C{str} : C{int}
    @param packages: dict of (packages: estimated runtime)
    
    @type max_runtime: C{int}
    @param max_runtime: returned groups of packages should not exceed
                        it when possible
                        
    @type max_groups: C{int} 
    @param max_groups: MUST be greater than 1, maximum number of groups
                       to be returned

    @rtype: C{list} of C{list} of C{str} 
    @returns: list of list of task names, each sublist is a group of packages, 
              total estimated runtime of a group should be below max_runtime
    """
    sorted_tasks, unknown_tasks = _sort_tasks(packages)
    tgroups = []

    # cmp will return 0 if there was no unknown tasks, 1 otherwise
    while sorted_tasks and (len(tgroups) < 
                            max_groups - cmp(unknown_tasks, [])):
        tgroups.append( _create_group(sorted_tasks, max_runtime) )

    # if not all tasks fit under runtime group limit
    i = 0
    while sorted_tasks:
        next_task = (i + 1) % len(tgroups)
        # find a group which runtime is shorter than next groups runtime
        while _group_runtime(tgroups[i]) <= _group_runtime(tgroups[next_task]) and \
                sorted_tasks:
            tgroups[i].append(sorted_tasks.pop())
        i = next_task

    # flatten groups
    groups = [[t[0] for t in g] for g in tgroups]

    if unknown_tasks:
        groups.append(unknown_tasks)
    return groups
    

def _group_runtime(group):
    """
    Total runtime for group
    """
    return sum(t[1] for t in group)


def _find_task(sorted_tasks, max_time):
    """
    Find task
    """
    matching_tasks = filter(lambda t: t[1] <= max_time, sorted_tasks)
    if matching_tasks:
        # filter() on sorted list returns sorted
        task = matching_tasks[-1]
        sorted_tasks.remove(task)
        return task
    else:
        return None


def _create_group(sorted_tasks, max_runtime):
    """
    Creates a group of tasks adding longest possible tasks one by one
    Group exceeds max_runtime only if it had single long task
    """
    task = sorted_tasks.pop()
    group = [task]
    runtime = _group_runtime(group)
    while runtime < max_runtime:
        task = _find_task(sorted_tasks, max_runtime-runtime)
        if task:
            group.append(task)
            runtime = _group_runtime(group)
        else:
            break
    return group


def _sort_tasks(tasks):
    """
    Sort tasks
    """
    estimated = [(t, tasks[t]) for t in tasks if tasks[t] != None]
    not_estimated = [t for t in tasks if tasks[t] == None]
    estimated.sort(lambda t1, t2: cmp(t1[1], t2[1]))
    return estimated, not_estimated
