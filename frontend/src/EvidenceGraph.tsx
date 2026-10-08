
import { useMemo, useState } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MarkerType,
  Position,
  type Node,
  type Edge,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

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

type Props = {
  nodes: EvidenceNode[]
  edges: EvidenceEdge[]
}

function formatLabel(value: string) {
  return value
    .replaceAll('_', ' ')
    .replace(/\b\w/g, char => char.toUpperCase())
}

function formatCode(value: unknown) {
  return typeof value === 'number' ? String(value) : 'Unavailable'
}

function EvidenceDetails({ node }: { node: EvidenceNode }) {
  const data = node.data

  if (node.type === 'experiment') {
    const verified = data.verified === true
    const beforeCode = data.before_return_code
    const afterCode = data.after_return_code

    return (
      <div className="evidence-details">
        <h4>Commit Reversal Verification</h4>

        <p>
          <strong>Verification result: </strong>
          <span style={{ color: verified ? '#4ade80' : '#fbbf24' }}>
            {verified ? 'REVERSAL VERIFIED' : 'INCONCLUSIVE'}
          </span>
        </p>

        <div className="experiment-results">
          <div className="experiment-result">
            <span>Before Reversal</span>
            <strong>
              {beforeCode === 1
                ? 'TEST FAILED'
                : `Exit code: ${formatCode(beforeCode)}`}
            </strong>
            <small>Original suspected revision</small>
          </div>

          <div className="experiment-result">
            <span>After Reversal</span>
            <strong>
              {afterCode === 0
                ? 'TEST PASSED'
                : `Exit code: ${formatCode(afterCode)}`}
            </strong>
            <small>Suspected change reversed</small>
          </div>
        </div>

        <p>
          {verified
            ? 'Reversing the suspected change restored passing tests. This provides experimental evidence that the change contributed to the regression.'
            : 'The reversal experiment did not establish that the suspected change caused the test failure.'}
        </p>
      </div>
    )
  }

  if (node.type === 'git_commit') {
    return (
      <div className="evidence-details">
        <h4>Suspected Regression Commit</h4>
        <p>
          <strong>Commit hash:</strong>
        </p>
        <code className="evidence-hash">
          {String(data.hash ?? 'Unknown')}
        </code>
        <p>
          This commit was selected for investigation based on
          the observed regression and Git history.
        </p>
      </div>
    )
  }

  if (node.type === 'test_failure') {
    return (
      <div className="evidence-details">
        <h4>Observed Test Failure</h4>
        <p>
          <strong>Exit code:</strong> {formatCode(data.return_code)}
        </p>
        <pre className="evidence-output">
          {String(data.output ?? 'No test output available')}
        </pre>
      </div>
    )
  }

  if (node.type === 'ai_hypothesis') {
    return (
      <div className="evidence-details">
        <h4>NVIDIA Nemotron Hypothesis</h4>
        <p>
          <strong>Model:</strong> {String(data.model ?? 'Unknown')}
        </p>
        <p>
          This is the AI-generated explanation. Experimental
          verification is recorded separately.
        </p>
        <pre className="evidence-output">
          {String(data.explanation ?? 'No explanation available')}
        </pre>
      </div>
    )
  }

  return (
    <pre className="evidence-output">
      {JSON.stringify(data, null, 2)}
    </pre>
  )
}

export default function EvidenceGraph({ nodes, edges }: Props) {
  const [selectedNode, setSelectedNode] = useState<EvidenceNode | null>(null)

  const flowNodes = useMemo<Node[]>(
    () =>
      nodes.map((node, index) => ({
        id: node.id,
        position: {
          x: 200,
          y: index * 160,
        },
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
        data: {
          label: formatLabel(node.id),
        },
        style: {
          background: '#252e49',
          color: '#ffffff',
          border: '1px solid #818cf8',
          borderRadius: '12px',
          padding: '18px',
          width: 260,
          fontWeight: 600,
          textAlign: 'center' as const,
        },
      })),
    [nodes]
  )

  const flowEdges = useMemo<Edge[]>(
    () =>
      edges.map((edge, index) => ({
        id: `edge-${index}`,
        source: edge.source,
        target: edge.target,
        type: 'smoothstep',
        label: edge.relationship.replaceAll('_', ' '),
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#818cf8',
        },
        style: {
          stroke: '#818cf8',
          strokeWidth: 2,
        },
        labelStyle: {
          fill: '#cbd5e1',
          fontSize: 11,
        },
        labelBgStyle: {
          fill: '#252e49',
        },
        labelBgPadding: [8, 5],
        labelBgBorderRadius: 6,
      })),
    [edges]
  )

  return (
    <div>
      <div style={{ height: 650, width: '100%' }}>
        <ReactFlow
          nodes={flowNodes}
          edges={flowEdges}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          nodesDraggable
          nodesConnectable={false}
          elementsSelectable
          colorMode="dark"
          onNodeClick={(_, clickedNode) => {
            const selected = nodes.find(
              node => node.id === clickedNode.id
            )
            setSelectedNode(selected ?? null)
          }}
        >
          <Background color="#334155" gap={20} />
          <Controls />
        </ReactFlow>
      </div>

      {selectedNode && (
        <section className="evidence-inspector">
          <div className="evidence-inspector-header">
            <div>
              <h3>{formatLabel(selectedNode.id)}</h3>
              <p>
                Evidence type: {formatLabel(selectedNode.type)}
              </p>
            </div>

            <button
              type="button"
              className="evidence-close"
              onClick={() => setSelectedNode(null)}
            >
              Close
            </button>
          </div>

          <EvidenceDetails node={selectedNode} />
        </section>
      )}
    </div>
  )
}
