from __future__ import annotations

from sklearn.preprocessing import StandardScaler as sk_StandardScaler

from safeds.data.tabular.containers import Table
from safeds.data.tabular.transformation._table_transformer import InvertibleTableTransformer
from safeds.exceptions import TransformerNotFittedError, UnknownColumnNameError


class StandardScaler(InvertibleTableTransformer):
    """The StandardScaler transforms column values by scaling each value to a given range."""

    def __init__(self) -> None:
        self._column_names: list[str] | None = None
        self._wrapped_transformer: sk_StandardScaler | None = None

    def fit(self, table: Table, column_names: list[str] | None) -> StandardScaler:
        """
        Learn a transformation for a set of columns in a table.

        This transformer is not modified.

        Parameters
        ----------
        table : Table
            The table used to fit the transformer.
        column_names : Optional[list[str]]
            The list of columns from the table used to fit the transformer. If `None`, all columns are used.

        Returns
        -------
        fitted_transformer : TableTransformer
            The fitted transformer.
        """
        if column_names is None:
            column_names = table.column_names
        else:
            missing_columns = set(column_names) - set(table.column_names)
            if len(missing_columns) > 0:
                raise UnknownColumnNameError(list(missing_columns))

        wrapped_transformer = sk_StandardScaler()
        wrapped_transformer.fit(table._data[column_names])

        result = StandardScaler()
        result._wrapped_transformer = wrapped_transformer
        result._column_names = column_names

        return result

    def transform(self, table: Table) -> Table:
        """
        Apply the learned transformation to a table.

        The table is not modified.

        Parameters
        ----------
        table : Table
            The table to which the learned transformation is applied.

        Returns
        -------
        transformed_table : Table
            The transformed table.

        Raises
        ------
        TransformerNotFittedError
            If the transformer has not been fitted yet.
        """
        # Transformer has not been fitted yet
        if self._wrapped_transformer is None or self._column_names is None:
            raise TransformerNotFittedError

        # Input table does not contain all columns used to fit the transformer
        missing_columns = set(self._column_names) - set(table.column_names)
        if len(missing_columns) > 0:
            raise UnknownColumnNameError(list(missing_columns))

        data = table._data.copy()
        data.columns = table.column_names
        data[self._column_names] = self._wrapped_transformer.transform(data[self._column_names])
        return Table._from_pandas_dataframe(data)

    def inverse_transform(self, transformed_table: Table) -> Table:
        """
        Undo the learned transformation.

        The table is not modified.

        Parameters
        ----------
        transformed_table : Table
            The table to be transformed back to the original version.

        Returns
        -------
        table : Table
            The original table.

        Raises
        ------
        TransformerNotFittedError
            If the transformer has not been fitted yet.
        """
        # Transformer has not been fitted yet
        if self._wrapped_transformer is None or self._column_names is None:
            raise TransformerNotFittedError

        data = transformed_table._data.copy()
        data.columns = transformed_table.column_names
        data[self._column_names] = self._wrapped_transformer.inverse_transform(data[self._column_names])
        return Table._from_pandas_dataframe(data)

    def is_fitted(self) -> bool:
        """
        Check if the transformer is fitted.

        Returns
        -------
        is_fitted : bool
            Whether the transformer is fitted.
        """
        return self._wrapped_transformer is not None

    def get_names_of_added_columns(self) -> list[str]:
        """
        Get the names of all new columns that have been added by the StandardScaler.

        Returns
        -------
        added_columns : list[str]
            A list of names of the added columns, ordered as they will appear in the table.

        Raises
        ------
        TransformerNotFittedError
            If the transformer has not been fitted yet.
        """
        if not self.is_fitted():
            raise TransformerNotFittedError
        return []

    # (Must implement abstract method, cannot instantiate class otherwise.)
    def get_names_of_changed_columns(self) -> list[str]:
        """
         Get the names of all columns that may have been changed by the StandardScaler.

        Returns
        -------
        changed_columns : list[str]
             The list of (potentially) changed column names, as passed to fit.

        Raises
        ------
        TransformerNotFittedError
            If the transformer has not been fitted yet.
        """
        if self._column_names is None:
            raise TransformerNotFittedError
        return self._column_names

    def get_names_of_removed_columns(self) -> list[str]:
        """
        Get the names of all columns that have been removed by the StandardScaler.

        Returns
        -------
        removed_columns : list[str]
            A list of names of the removed columns, ordered as they appear in the table the StandardScaler was fitted on.

        Raises
        ------
        TransformerNotFittedError
            If the transformer has not been fitted yet.
        """
        if not self.is_fitted():
            raise TransformerNotFittedError
        return []