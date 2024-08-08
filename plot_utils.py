import numpy as np
import matplotlib.pyplot as plt
from utils import condense_amounts

global_plot = None

class AdvancedPiePlot:
    subfig = None
    subax = None
    subtexts = None
    plotted_amounts = None 
    plotted_labels = None


    def __init__(self, umsatz_cat, weeks) -> None:
        global global_plot
        self.umsatz_cat = umsatz_cat
        self.weeks = weeks
        self.fig = plt.figure()
        self.ax = plt.subplot()
        global_plot = self
    
    def sort(self, amounts, labels):
        sort_ind = list(reversed(np.argsort(amounts)))
        amounts = np.array(amounts)[sort_ind]
        labels = np.array(labels)[sort_ind]
        return amounts, labels

    def plot(self, amounts, labels):
        amounts, labels = self.sort(amounts, labels)
        explode = [0.1] * len(amounts)
        self.patches, self.texts = self.ax.pie(amounts, labels=labels, explode=explode)

    def finalize(self):
        self.fig.canvas.mpl_connect("motion_notify_event", AdvancedPiePlot.hover)
        self.fig.canvas.mpl_connect("button_press_event", AdvancedPiePlot.onclick)
        plt.show()

    def add_annotations(self):
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="white", ec="b", lw=2))
        #                    arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)

    def update_annotations(self, patch, keywords, counts, total):
        self.annot.xy = patch.center
        sort_index = np.argsort(counts)
        text = ""
        for i in reversed(range(len(keywords))):
            index = sort_index[i]
            text += keywords[index]
            if counts[index] > 1:
                text += f" x{counts[index]}"
            #if i > 0:
            text += "\n"
        text += f"\n{total:.2f}€ pro Woche"
        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_alpha(0.8)

    def plot_category(self, cat, cat_data):
        self.subfig = plt.figure()
        self.subax = plt.subplot()
        amounts = cat_data["amounts"]
        labels = cat_data["labels"]
        labels, amounts = condense_amounts(labels, amounts)
        amounts, labels = self.sort(amounts, labels)
        explode = [0.1] * len(amounts)
        self.patches, self.subtexts = self.subax.pie(amounts, labels=labels, explode=explode)
        self.plotted_labels = labels
        self.plotted_amounts = amounts
        
        plt.title(cat)
        self.subfig.canvas.mpl_connect("motion_notify_event", AdvancedPiePlot.hover_category)
        plt.show()

    @staticmethod
    def hover(event):
        self = global_plot
        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            for i in range(len(self.patches)):
                patch = self.patches[i]
                cont, ind = patch.contains(event)
                if cont:
                    cat = self.texts[i].get_text()
                    labels = self.umsatz_cat[cat]["labels"]
                    keywords, counts = np.unique(labels, return_counts=True)
                    self.update_annotations(patch, keywords, counts, self.umsatz_cat[cat]["total"] / self.weeks)
                    self.annot.set_visible(True)
                    self.fig.canvas.draw_idle()
                    return
        if vis:
            self.annot.set_visible(False)
            self.fig.canvas.draw_idle()
            
    @staticmethod
    def hover_category(event):
        self = global_plot
        vis = self.annot.get_visible()
        if event.inaxes == self.subax:
            for i in range(len(self.patches)):
                patch = self.patches[i]
                cont, ind = patch.contains(event)
                if cont:
                    keyword = self.subtexts[i].get_text()
                    i_keyword = self.plotted_labels.index(keyword)
                    amount = self.plotted_amounts[i_keyword]
                    self.annot.xy = patch.center
                    self.annot.set_text(f"{amount:.2f}€\n{amount / self.weeks:.2f}€ pro Woche")
                    self.annot.get_bbox_patch().set_alpha(0.8)
                    self.annot.set_visible(True)
                    self.subfig.canvas.draw_idle()
                    return
        if vis:
            self.annot.set_visible(False)
            self.subfig.canvas.draw_idle()
            
    @staticmethod
    def onclick(event):
        self = global_plot
        if event.inaxes == self.ax:
            for i in range(len(self.patches)):
                patch = self.patches[i]
                cont, ind = patch.contains(event)
                if cont:
                    cat = self.texts[i].get_text()
                    self.plot_category(cat, self.umsatz_cat[cat])
                    return
                

class AdvancedLinePlot:
    def __init__(self) -> None:
        self.fig = plt.figure()
        self.ax = plt.subplot()

    def plot(self, months, amounts, label=None):
        self.ax.plot(months, amounts, label=label)

    def stackplot(self, x, y, labels):
        self.ax.stackplot(x, y, labels=labels)

    def finalize(self):
        ax = plt.gca()
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.show()