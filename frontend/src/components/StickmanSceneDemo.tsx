import { useMemo, useState } from "react";
import type { ScriptScenePreview } from "../services/api";

type StickmanSceneDemoProps = {
  scenes: ScriptScenePreview[];
};

type StickFigureProps = {
  name: string;
  emotion: string;
  side: "left" | "right";
};

function findEmotion(scene: ScriptScenePreview, characterName: string) {
  return scene.emotions.find((emotion) => emotion.character === characterName)?.emotion || "待表演";
}

function getDialogueLine(scene: ScriptScenePreview, speaker: string, fallbackIndex: number) {
  return (
    scene.dialogues.find((dialogue) => dialogue.speaker === speaker) ||
    scene.dialogues[fallbackIndex] || {
      speaker,
      line: "以动作推进剧情",
      emotion: ""
    }
  );
}

function StickFigure({ name, emotion, side }: StickFigureProps) {
  return (
    <div className={`stick-actor ${side}`}>
      <div className="speech-name">{name}</div>
      <div className="stick-body" aria-hidden="true">
        <span className="stick-head" />
        <span className="stick-torso" />
        <span className="stick-arm left-arm" />
        <span className="stick-arm right-arm" />
        <span className="stick-leg left-leg" />
        <span className="stick-leg right-leg" />
      </div>
      <div className="emotion-chip">{emotion}</div>
    </div>
  );
}

export function StickmanSceneDemo({ scenes }: StickmanSceneDemoProps) {
  const [selectedSceneId, setSelectedSceneId] = useState("");

  const activeScene = useMemo(() => {
    if (scenes.length === 0) {
      return null;
    }
    return scenes.find((scene) => scene.scene_id === selectedSceneId) || scenes[0];
  }, [scenes, selectedSceneId]);

  if (!activeScene) {
    return null;
  }

  const actors = activeScene.characters_in_scene.length > 0 ? activeScene.characters_in_scene.slice(0, 2) : ["旁白"];
  const leftActor = actors[0] || "角色一";
  const rightActor = actors[1] || "旁白";
  const leftDialogue = getDialogueLine(activeScene, leftActor, 0);
  const rightDialogue = getDialogueLine(activeScene, rightActor, 1);
  const narration = activeScene.narration[0]?.text || activeScene.summary;
  const conflict = activeScene.conflicts[0] || activeScene.plot_points[0] || "当前场景暂无明确冲突";
  const transitionText = activeScene.transition.description || activeScene.transition.type || "等待下一场";

  return (
    <div className="preview-section stickman-section">
      <div className="panel-heading compact-heading">
        <h2>火柴人片段演示</h2>
      </div>

      <div className="scene-switcher" aria-label="选择演示场景">
        {scenes.slice(0, 4).map((scene) => (
          <button
            key={scene.scene_id}
            type="button"
            className={activeScene.scene_id === scene.scene_id ? "active" : ""}
            onClick={() => setSelectedSceneId(scene.scene_id)}
          >
            {scene.scene_id}
          </button>
        ))}
      </div>

      <div className="mini-stage" aria-label={`${activeScene.scene_id} 场景动画`}>
        <div className="stage-meta">
          <strong>{activeScene.location}</strong>
          <span>{activeScene.time}</span>
        </div>
        <div className="speech-bubble left">
          <strong>{leftDialogue.speaker}</strong>
          <span>{leftDialogue.line}</span>
        </div>
        {actors.length > 1 ? (
          <div className="speech-bubble right">
            <strong>{rightDialogue.speaker}</strong>
            <span>{rightDialogue.line}</span>
          </div>
        ) : null}
        <StickFigure name={leftActor} emotion={findEmotion(activeScene, leftActor)} side="left" />
        {actors.length > 1 ? (
          <StickFigure name={rightActor} emotion={findEmotion(activeScene, rightActor)} side="right" />
        ) : null}
        <div className="stage-floor" />
      </div>

      <div className="cue-grid">
        <div>
          <span>旁白</span>
          <p>{narration}</p>
        </div>
        <div>
          <span>冲突</span>
          <p>{conflict}</p>
        </div>
        <div>
          <span>动作</span>
          <p>{activeScene.actions[0]?.description || "暂无动作描写"}</p>
        </div>
        <div>
          <span>转场</span>
          <p>{transitionText}</p>
        </div>
      </div>
    </div>
  );
}
