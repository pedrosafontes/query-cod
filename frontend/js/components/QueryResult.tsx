import { QueryResultData } from "js/api";
import { Alert, Table } from "react-bootstrap";

const QueryResult = ({ success, result }: { success: boolean; result: QueryResultData | undefined }) => {
  if (!success) {
    return (
      <Alert variant="danger" className="mb-0">
        Query execution failed.
      </Alert>
    );
  } else if (result) {
    if (result.columns.length == 0) {
      return (
        <Alert variant="warning" className="mb-0">
          No results found.
        </Alert>
      );
    }

    return (
      <div className="rounded border overflow-hidden">
        <Table responsive className="mb-0">
          <thead>
            <tr>
              {result.columns.map((column: string, index: number) => (
                <th key={column}>{column}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {result.rows.map((row, index: number) => (
              <tr key={index}>
                {row.map((cell: string | null, cellIndex: number) => (
                  <td key={`${index}-${cellIndex}`}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </Table>
      </div>
    );
  }
};

export default QueryResult;
