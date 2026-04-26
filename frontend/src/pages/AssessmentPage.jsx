import { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { Send, Play, CheckCircle } from 'lucide-react';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import SectionHeader from '../components/ui/SectionHeader';

const initialCode = 'def reverse_string(s):\n    # Write your code here\n    pass';

export default function AssessmentPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    {
      role: 'agent',
      content:
        "Welcome to your technical assessment. Let's begin with a Python challenge: write a function that reverses text.",
    },
  ]);
  const [input, setInput] = useState('');
  const [code, setCode] = useState(initialCode);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const appendMessage = (message) => {
    setMessages((prev) => [...prev, message]);
  };

  const handleSend = () => {
    if (!input.trim()) {
      setError('Write a reply before sending.');
      return;
    }

    setError('');
    setIsSending(true);
    appendMessage({ role: 'user', content: input });
    setInput('');

    setTimeout(() => {
      appendMessage({
        role: 'agent',
        content:
          'Nice work — keep it up. Next, tell me about a time you improved a production system or optimized an algorithm.',
      });
      setIsSending(false);
    }, 1100);
  };

  const finishAssessment = () => {
    navigate(`/dashboard/${sessionId ?? 'test-session-123'}`);
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[1.4fr_0.9fr]">
      <div className="space-y-6">
        <SectionHeader
          eyebrow="Live assessment"
          title="Interactive AI interview"
          description="Answer questions, refine your code, and see instant conversational feedback from the virtual interviewer."
        />

        <Card>
          <div className="flex items-center justify-between gap-3 pb-4 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <span className="flex h-3 w-3 rounded-full bg-emerald-400 shadow-[0_0_0_8px_rgba(16,185,129,0.08)]" />
              <div>
                <p className="text-sm uppercase tracking-[0.25em] text-slate-500">AI Interviewer</p>
                <p className="text-sm text-slate-400">Live conversation session</p>
              </div>
            </div>
            <Button variant="secondary" onClick={finishAssessment} aria-label="Finish assessment">
              <CheckCircle size={16} />
              Finish
            </Button>
          </div>

          <div className="space-y-4 overflow-hidden rounded-3xl bg-slate-950/90 p-4 text-sm text-slate-300 shadow-inner shadow-slate-950/30">
            <div className="flex flex-col gap-4 overflow-y-auto max-h-[420px] pr-2">
              {messages.map((message, index) => {
                const isUser = message.role === 'user';
                return (
                  <div key={index} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                    <div
                      className={`max-w-[84%] rounded-3xl border px-4 py-3 text-sm ${
                        isUser
                          ? 'bg-slate-700 text-slate-100 border-slate-600 rounded-br-none'
                          : 'bg-slate-800 text-slate-100 border-slate-700 rounded-bl-none'
                      }`}
                      role="article"
                      aria-label={isUser ? 'Your message' : 'Agent response'}
                    >
                      <p>{message.content}</p>
                      {message.code && (
                        <pre className="mt-3 overflow-x-auto rounded-2xl bg-slate-900 px-3 py-3 text-xs text-slate-200">
                          <code>{message.code}</code>
                        </pre>
                      )}
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>
          </div>

          <div className="space-y-3 pt-4">
            {error && <p className="text-sm text-rose-400">{error}</p>}
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
              <label htmlFor="assessment-input" className="sr-only">
                Your response
              </label>
              <textarea
                id="assessment-input"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                rows={3}
                placeholder="Type your answer here..."
                className="min-h-[120px] flex-1 rounded-3xl border border-slate-700 bg-slate-950/90 p-4 text-sm text-slate-100 outline-none transition focus:border-amber-400 focus:ring-2 focus:ring-amber-400/20"
              />
              <Button
                onClick={handleSend}
                disabled={isSending}
                className="min-w-[160px]"
                aria-label="Send response"
              >
                {isSending ? 'Sending…' : <><Send size={16} /> Send</>}
              </Button>
            </div>
          </div>
        </Card>
      </div>

      <div className="space-y-6">
        <Card title="Code workspace" subtitle="Edit and test your solution in a clean editor area.">
          <div className="h-[520px] overflow-hidden rounded-[28px] border border-slate-800 bg-slate-950/95 shadow-[0_36px_70px_rgba(15,23,42,0.24)]">
            <Editor
              height="100%"
              defaultLanguage="python"
              defaultValue={initialCode}
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value ?? '')}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                automaticLayout: true,
              }}
            />
          </div>
          <div className="flex items-center justify-between gap-4 text-sm text-slate-400">
            <span>Use the console to refine your answer before finishing the assessment.</span>
            <Button variant="ghost" className="gap-2 text-slate-300 hover:text-white">
              <Play size={16} /> Run code
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}

            <span>Finish</span>
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl p-4 ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-slate-700 text-slate-100 rounded-bl-none'}`}>
                <p>{msg.content}</p>
                {msg.code && (
                  <pre className="mt-2 bg-slate-900 p-2 rounded-lg text-sm overflow-x-auto border border-slate-600">
                    <code>{msg.code}</code>
                  </pre>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 border-t border-slate-700 bg-slate-800/80">
          <div className="flex items-center space-x-2">
            <button className="p-3 bg-slate-700 hover:bg-slate-600 rounded-xl transition-colors group">
              <Mic className="w-5 h-5 text-slate-400 group-hover:text-blue-400" />
            </button>
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type your response..."
              className="flex-1 bg-slate-900 border border-slate-600 rounded-xl px-4 py-3 focus:outline-none focus:border-blue-500"
            />
            <button onClick={handleSend} className="p-3 bg-blue-600 hover:bg-blue-500 rounded-xl transition-colors">
              <Send className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>
      </div>

      {/* Code Editor Section */}
      <div className="flex-1 flex flex-col bg-slate-800/50 border border-slate-700 rounded-2xl overflow-hidden shadow-xl hidden md:flex">
        <div className="p-4 border-b border-slate-700 bg-slate-800 flex justify-between items-center">
          <h2 className="font-semibold text-slate-300">Code Workspace</h2>
          <button className="text-sm bg-green-600/20 text-green-400 hover:bg-green-600/30 px-3 py-1 rounded-lg flex items-center space-x-1 transition-colors">
            <Play className="w-4 h-4" />
            <span>Run Code</span>
          </button>
        </div>
        <div className="flex-1 relative">
          <Editor
            height="100%"
            defaultLanguage="python"
            theme="vs-dark"
            value={code}
            onChange={(value) => setCode(value || '')}
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              padding: { top: 16 },
              scrollBeyondLastLine: false,
            }}
          />
        </div>
      </div>
    </div>
  );
}
