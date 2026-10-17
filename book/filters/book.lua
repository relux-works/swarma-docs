-- Pandoc filter for the Swarma book.
--
-- 1. Status markers. The chapters write a status as ⟦решено⟧, which reads
--    cleanly on GitHub; in the book it becomes a coloured badge
--    <span class="status dec">решено</span>. A marker may span several words
--    (⟦работает сегодня⟧) and may carry punctuation before or after it.
-- 2. Diagram sizes. Tall diagrams get the class "tall" so that the
--    stylesheet lets them use the full page height.
-- 3. Landscape figures, see below.

local status_class = {
  ["работает сегодня"] = "now",
  ["решено"] = "dec",
  ["предложено"] = "prop",
  ["спецификация"] = "spec",
  ["открыто"] = "open",
}

local open_mark, close_mark = "⟦", "⟧"

local function badge(label)
  local class = status_class[label]
  if not class then
    error("unknown status marker: " .. label)
  end
  return pandoc.Span({ pandoc.Str(label) }, { class = "status " .. class })
end

-- Rewrite one run of inlines that starts with a Str containing the opening
-- mark. Returns the replacement inlines and the index after the run, or nil
-- when the run is not a complete marker.
local function take_marker(inlines, i)
  local parts = {}
  local j = i
  while j <= #inlines do
    local el = inlines[j]
    if el.t == "Str" then
      parts[#parts + 1] = el.text
      if el.text:find(close_mark, 1, true) then
        local s = table.concat(parts)
        local pre, label, post = s:match("^(.-)" .. open_mark .. "(.-)" .. close_mark .. "(.*)$")
        if not label then
          return nil
        end
        local out = pandoc.List()
        if pre ~= "" then out:insert(pandoc.Str(pre)) end
        out:insert(badge(label))
        if post ~= "" then out:insert(pandoc.Str(post)) end
        return out, j + 1
      end
    elseif el.t == "Space" or el.t == "SoftBreak" then
      parts[#parts + 1] = " "
    else
      return nil
    end
    j = j + 1
  end
  return nil
end

function Inlines(inlines)
  local out = pandoc.List()
  local i = 1
  while i <= #inlines do
    local el = inlines[i]
    local replaced, next_i = nil, nil
    if el.t == "Str" and el.text:find(open_mark, 1, true) then
      replaced, next_i = take_marker(inlines, i)
    end
    if replaced then
      out:extend(replaced)
      i = next_i
    else
      out:insert(el)
      i = i + 1
    end
  end
  return out
end

local tall = {
  ["bridge-components"] = true,
  ["board-components"] = true,
}

function Image(img)
  local name = img.src:match("([^/]+)%.png$")
  if name and tall[name] then
    img.classes:insert("tall")
  end
  return img
end

-- 3. Landscape figures. An image marked {.landscape} puts its whole figure
--    on a landscape page (the stylesheet selects the page by the class).
function Figure(fig)
  local landscape = false
  fig:walk({ Image = function(img)
    if img.classes:includes("landscape") then landscape = true end
  end })
  if landscape then
    fig.classes:insert("landscape")
  end
  return fig
end
