# vision-agents 調査結果と解決策

## 調査結果

### 確認できたこと

1. ✅ `vision_agents.core` - コア機能は正常にインストールされている
2. ✅ `vision_agents.core.agents.Agent` - Agentクラスは存在
3. ✅ `vision_agents.core.llm.realtime.Realtime` - Gemini Realtime LLMは存在
4. ✅ `vision_agents.core.processors.Processor` - Processorベースクラスは存在
5. ❌ `vision_agents.plugins` - **このモジュールが存在しない**

### 問題点

`personal_gym_trainer.py`では以下のインポートを試みていますが、失敗します：

```python
from vision_agents.plugins import getstream, ultralytics, gemini
```

しかし、`agents.py`のコードでは：
```python
if TYPE_CHECKING:
    from vision_agents.plugins.getstream.stream_edge_transport import StreamEdge
```

これは型チェック用のインポートで、実行時には評価されません。

### Agentクラスの要件

```python
Agent(
    edge: "StreamEdge",  # StreamEdge型が必要
    llm: LLM | AudioLLM | VideoLLM,
    agent_user: User,
    instructions: str,
    processors: List[Processor] | None = None,
    ...
)
```

## 解決策

### オプション1: vision-agentsのGitHubリポジトリを確認

公式リポジトリでプラグインのインストール方法を確認：
- https://github.com/getstream-io/vision-agents
- プラグインが別パッケージとして提供されている可能性

### オプション2: 代替実装を作成

`StreamEdge`の代わりに、`EdgeTransport`を継承した実装を作成するか、`getstream`パッケージから直接必要な機能を使用する。

### オプション3: 公式ドキュメントを確認

`vision-agents`の公式ドキュメントで正しい使用方法を確認：
- https://visionagents.ai/
- サンプルコードやチュートリアルを参照

## 推奨される次のステップ

1. **GitHubリポジトリを確認**
   ```bash
   # リポジトリをクローンして構造を確認
   git clone https://github.com/getstream-io/vision-agents.git
   cd vision-agents
   ls -la
   ```

2. **公式ドキュメントを確認**
   - サンプルコードを探す
   - プラグインのインストール方法を確認

3. **一時的な回避策**
   - Webダッシュボード（`gym_dashboard.py`）は動作する
   - AIトレーナー機能は`vision-agents`の正しい使用方法を確認後に実装

## 現在動作する機能

✅ Webダッシュボード (`gym_dashboard.py`)
- ユーザー管理
- トレーニング履歴表示
- 統計表示

❌ AIトレーナー (`personal_gym_trainer.py`)
- `vision-agents`のプラグイン問題により、現在は動作しない

