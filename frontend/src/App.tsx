
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useEffect, useState } from 'react'
import './App.css'
import EvidenceGraph from './EvidenceGraph'

type EvidenceNode = {
  id: string
  type: string
  data: Record<string, unknown>
}

type EvidenceEdge = {
  source: string
  target: string
  relationship: string
}

type EvidenceGraph = {
  created_at: string
  nodes: EvidenceNode[]
  edges: EvidenceEdge[]
}

function App() {
  const [graph, setGraph] = useState<EvidenceGraph | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    async function loadGraph() {
      try {
        const response = await fetch('/api/graph', {
          cache: 'no-store',
        })

        if (!response.ok) {
          throw new Error(`API returned ${response.status}`)
        }

        const data: EvidenceGraph = await response.json()
        setGraph(data)
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Unable to load graph'
        )
      } finally {
        setLoading(false)
      }
    }

    void loadGraph()
  }, [])

  async function runInvestigation() {
    if (running) return

    setRunning(true)
    setError(null)
    setSuccess(null)

    try {
      const response = await fetch('/api/run-investigation', {
        method: 'POST',
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)

        throw new Error(
          typeof errorData?.detail === 'string'
            ? errorData.detail
            : errorData?.detail?.message ??
              `Investigation failed (${response.status})`
        )
      }

      const graphResponse = await fetch('/api/graph', {
        cache: 'no-store',
      })

      if (!graphResponse.ok) {
        throw new Error(
          'Investigation completed, but the Evidence Graph could not be loaded.'
        )
      }

      const updatedGraph: EvidenceGraph = await graphResponse.json()

      setGraph(updatedGraph)
      setSuccess('Investigation completed. Evidence Graph updated.')
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Investigation failed'
      )
    } finally {
      setRunning(false)
    }
  }

  const failure = graph?.nodes.find(node => node.type === 'test_failure')
  const commit = graph?.nodes.find(node => node.type === 'git_commit')
  const hypothesis = graph?.nodes.find(node => node.type === 'ai_hypothesis')
  const experiment = graph?.nodes.find(node => node.type === 'experiment')

  return (
    <main className="dashboard">
      <header className="header">
        <div>
          <p className="eyebrow">AI-POWERED REGRESSION INVESTIGATION</p>
          <h1>CausalTrace</h1>
          <p className="subtitle">
            Don't guess why software failed. Investigate the evidence.
          </p>
        </div>

        <div className="header-actions">
          <span className="status">Investigation Dashboard</span>

          <button
            type="button"
            className="run-button"
            onClick={() => void runInvestigation()}
            disabled={running || loading}
          >
            {running ? 'Investigating...' : 'Run Investigation'}
          </button>
        </div>
      </header>

      {loading && <p>Loading investigation...</p>}

      {running && (
        <p role="status" className="investigation-progress">
          Running tests, examining Git history, generating the NVIDIA
          Nemotron hypothesis, and verifying the suspected regression...
        </p>
      )}

      {error && (
        <p role="alert" className="error">
          Error: {error}
        </p>
      )}

      {success && (
        <p role="status" className="investigation-success">
          {success}
        </p>
      )}

      {graph && (
        <>
          <section className="stats">
            <article className="card">
              <h3>Evidence Nodes</h3>
              <strong>{graph.nodes.length}</strong>
            </article>

            <article className="card">
              <h3>Evidence Connections</h3>
              <strong>{graph.edges.length}</strong>
            </article>

            <article className="card">
              <h3>Reversal Verification</h3>
              <strong>
                {experiment?.data.verified === true
                  ? 'VERIFIED'
                  : 'INCONCLUSIVE'}
              </strong>
            </article>
          </section>

          <section className="panel">
            <h2>Regression Investigation</h2>

            <p>
              <b>Suspected commit:</b>{' '}
              {String(commit?.data.hash ?? 'Unknown')}
            </p>

            <p>
              <b>Test status:</b> {failure ? 'FAILED' : 'Unknown'}
            </p>

            <p>
              <b>Verification:</b>{' '}
              {experiment?.data.verified === true
                ? 'Reversal restored passing tests'
                : 'Not verified'}
            </p>
          </section>

          <section className="panel">
            <h2>NVIDIA Nemotron Root-Cause Analysis</h2>

            <div className="analysis">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {String(
                  hypothesis?.data.explanation ??
                  'No analysis available'
                )}
              </ReactMarkdown>
            </div>
          </section>

          <section className="panel">
            <h2>Evidence Graph</h2>

            <EvidenceGraph
              nodes={graph.nodes}
              edges={graph.edges}
            />
          </section>
        </>
      )}
    </main>
  )
}

export default App
