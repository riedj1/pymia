import abc
import pickle

import numpy as np


class Assembler(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def add_sample(self, prediction, batch: dict):
        pass


class SubjectAssembler(Assembler):
    """Assembles predictions of one or multiple subjects."""

    def __init__(self):
        self.predictions = {}
        self.subjects_ready = set()

    def add_sample(self, prediction, batch: dict):
        if 'subject' not in batch:
            raise ValueError('SubjectAssembler requires "subject" to be extracted (use SubjectExtractor)')
        if 'index_expr' not in batch:
            raise ValueError('SubjectAssembler requires "index_expr" to be extracted (use IndexingExtractor)')
        if 'shape' not in batch:
            raise ValueError('SubjectAssembler requires "shape" to be extracted (use ShapeExtractor)')

        for idx, subject in enumerate(batch['subject']):
            # initialize subject
            if subject not in self.predictions and not self.predictions:
                self.predictions[subject] = np.zeros(batch['shape'][idx])
            elif subject not in self.predictions:
                self.subjects_ready = set(self.predictions.keys())
                self.predictions[subject] = np.zeros(batch['shape'][idx])

            index_expr = batch['index_expr'][idx]
            if isinstance(index_expr, str):
                # is pickled
                index_expr = pickle.loads(index_expr)
            self.predictions[subject][index_expr.expression] = prediction[index_expr.expression]

    def get_subject(self, subject: str):
        """Gets the prediction of a subject.

        Args:
            subject (str): The subject.

        Returns:
            np.ndarray: The prediction of the subject.
        """
        try:
            self.subjects_ready.remove(subject)
        except KeyError:
            # check if subject is assembled but not listed as ready
            # this can happen if only one subject was assembled
            if subject not in self.predictions:
                raise ValueError('Subject "{}" not in assembler'.format(subject))
        return self.predictions.pop(subject)
