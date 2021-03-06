#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#@author: Aleksey Komissarov
#@contact: ad3002@gmail.com 

import simplejson
import argparse

class DialogTest(object):

    def __init__(self, d):
        self.id = d["dialogId"]
        self.context = d["context"]
        self.bob_q = 0
        self.alice_q = 0
        self.bob = "Bot"
        self.alice = "Bot"
        self.bobs = []
        self.alices = []
        self.dialog = []
        for i, x in enumerate(d["thread"]):
            if x["userId"] == "Bob":
                self.bobs.append((i,x["text"]))
                self.dialog.append(("bob", x["text"]))
            else:
                self.alices.append((i,x["text"]))
                self.dialog.append(("alice", x["text"]))

        self.alice_txt = " ".join(["_%s_ %s" % (x[0],x[1]) for x in self.alices])
        self.bob_txt = " ".join(["_%s_ %s" % (x[0],x[1]) for x in self.bobs])

    def __str__(self):
        print self.alice, self.alice_q
        print self.alice_txt
        print self.bob, self.bob_q
        print self.bob_txt
        return ""





def refine(refineable_file, submit_file, test_files):
    data = []
    for test_file in test_files:
        with open(test_file) as fh:
            data += [DialogTest(x) for x in simplejson.load(fh)]

    with open(refineable_file) as fh:
        M = {}
        for line in fh:
            if line.startswith("dialogId"):
                continue
            if line.startswith("#"):
                continue
            d = line.strip().split(",")
            M[int(d[0])] = (float(d[1]),float(d[2]))
    for i, d in enumerate(data):
        if not d.id in M:
            raise Exception("Wrong test dataset: %s" % ",".join(test_files))
        data[i].alice_q = round(M[d.id][0],3)
        data[i].bob_q = round(M[d.id][1],3)

    for i, d in enumerate(data):

        if d.alice_q < 0:
            d.alice_q = 0.0
        if d.bob_q < 0:
            d.bob_q = 0.0

        if d.alices and d.alices[0][1].startswith("wtf"):
            d.alice_q = max(d.alice_q, 1.0)
            d.bob_q = 0.0
            continue

        if d.bobs and d.bobs[0][1].startswith("wtf"):
            d.bob_q = max(d.bob_q, 1.0)
            d.alice_q = 0.0
            continue

        if len(d.alices) == 0 and len(d.bobs) == 0:
            d.alice_q = 0.0
            d.bob_q = 1.0
            continue

        if len(d.alices) > 0 and len(d.bobs) == 0:
            if d.alices[0][1].startswith(" "):
                d.alice_q = 1.0
                d.bob_q = 0.0
            else:
                d.alice_q = 0.0
                d.bob_q = 1.0
            continue

        if len(d.alices) == 0 and len(d.bobs) > 0:
            if d.bobs[0][1].startswith(" "):
                d.alice_q = 0.0
                d.bob_q = 1.0
            else:
                d.alice_q = 1.0
                d.bob_q = 0.0
            continue

        alice_spaces = len([x for x in d.alices if x[1].startswith(" ")])
        if alice_spaces > 1:
            d.alice_q = max(d.alice_q, 1.0)
            d.bob_q = 0.0
            continue

        bob_spaces = len([x for x in d.bobs if x[1].startswith(" ")])
        if bob_spaces > 1:
            d.bob_q = max(d.bob_q, 1.0)
            d.alice_q = 0.0
            continue

        bot_marksers = [
            "Interesting fact",
            "Answer, amaze and amuse.",
            "I can answer your questions. Ask me anything!",
            # "\n",
            " .",
            # " ?",
            # " ,",
            # " \'",
            "/end",
            "/start",
            "<",
            " 's",
            "Talking is the best.",
            "I will ask you a question in a second, please wait.",
            "Congressional",
            "I don't understand what's",
        ]

        for x in bot_marksers:
            if x in d.alice_txt:
                d.alice_q = max(d.alice_q, 1.0)
                d.bob_q = 0.0
                break
            if x in d.bob_txt:
                d.bob_q = max(d.bob_q, 1.0)
                d.alice_q = 0.0
                break


    for i, d in enumerate(data):
        if d.alice_q < 1 and d.bob_q < 1:
            if d.alice_q <= d.bob_q:
                d.alice_q = 0.0
                d.bob_q = 1.0
            else:
                d.alice_q = 1.0
                d.bob_q = 0.0
            continue


    ### adjust to more positive score
    
    for i, d in enumerate(data):
    
        addjastment = 0.4
        max_possible = 4.0
        if len(d.alices) > 10:
            addjastment = 0.8
        elif len(d.alices) > 30:
            max_possible = 5.0
            addjastment = 1.2
        if d.alice_q > 1 and d.alice_q < max_possible:
            d.alice_q = min(max_possible, d.alice_q+addjastment)

        addjastment = 0.4
        max_possible = 4.0
        if len(d.bobs) > 10:
            addjastment = 0.8
        elif len(d.bobs) > 30:
            max_possible = 5.0
            addjastment = 1.2
        if d.bob_q > 1 and d.bob_q < max_possible:
            d.bob_q = min(max_possible, d.bob_q+addjastment)


    with open(submit_file, "w") as fh:
        for i, d in enumerate(data):
            fh.write("%s,%s,%s\n" % (d.id, d.alice_q, d.bob_q))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dialogs', type=str, required=True)
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    args = parser.parse_args()

    refine(args.input, args.output, [args.dialogs])











