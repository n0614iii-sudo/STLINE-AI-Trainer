# vision-agents プラグイン問題の調査結果

## 問題

`vision_agents.plugins`モジュールが見つかりません。しかし、`agents.py`では以下のインポートを試みています：

```python
from vision_agents.plugins.getstream.stream_edge_transport import StreamEdge
```

## 調査結果

1. **`vision-agents`パッケージの構造:**
   - `vision_agents.core` - コア機能（存在する）
   - `vision_agents.core.agents` - Agentクラス（存在する）
   - `vision_agents.core.llm` - LLMクラス（存在する、`Realtime`含む）
   - `vision_agents.core.processors` - Processorクラス（存在する）
   - `vision_agents.plugins` - **存在しない**

2. **Agentクラスのシグネチャ:**
   ```python
   Agent(
       edge: "StreamEdge",
       llm: LLM | AudioLLM | VideoLLM,
       agent_user: User,
       instructions: str = '...',
       processors: List[Processor] | None = None,
       ...
   )
   ```

3. **利用可能なクラス:**
   - `vision_agents.core.llm.realtime.Realtime` - Gemini Realtime LLM
   - `vision_agents.core.processors.Processor` - ベースプロセッサー
   - `vision_agents.core.edge.edge_transport.EdgeTransport` - Edge Transport

## 解決策の提案

### オプション1: プラグインディレクトリを手動で作成

`vision-agents`パッケージに`plugins`ディレクトリが含まれていない可能性があります。GitHubリポジトリから直接インストールするか、プラグインを別途インストールする必要があるかもしれません。

### オプション2: 直接インポートを使用

`StreamEdge`を直接作成するか、`EdgeTransport`を使用する実装に変更する。

### オプション3: vision-agentsのGitHubリポジトリを確認

公式リポジトリでプラグインのインストール方法を確認：
- https://github.com/getstream-io/vision-agents

## 次のステップ

1. `vision-agents`のGitHubリポジトリを確認
2. プラグインのインストール方法を特定
3. コードを修正

