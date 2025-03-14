// Component for showing group limits (total number of groups)
export const GroupLimit: React.FC<{ showAlways?: boolean }> = ({ showAlways = false }) => {
  const { value, getMaxTotalValues } = useNestedMapping();
  const groupCount = Object.keys(value).length;
  const maxGroups = getMaxTotalValues();

  return (
    <LimitCounter
      current={groupCount}
      max={maxGroups}
      label="Groups"
      showAlways={showAlways}
    />
  );
};

// Component for showing total values mapped (not in available values)
export const ValueLimit: React.FC<{ showAlways?: boolean }> = ({ showAlways = false }) => {
  const { value, getMaxTotalValues } = useNestedMapping();

  // Count total values across all groups
  let totalValues = 0;
  Object.values(value).forEach(group => {
    totalValues += group.values?.length || 0;
  });

  const maxValues = getMaxTotalValues();

  return (
    <LimitCounter
      current={totalValues}
      max={maxValues}
      label="Total Values"
      showAlways={showAlways}
    />
  );
};

// Component for showing per-group value limits
export const GroupValueLimit: React.FC<{ groupId: string, showAlways?: boolean }> = ({
  groupId,
  showAlways = false
}) => {
  const { value, getMaxValuesPerGroup } = useNestedMapping();

  if (!value[groupId]) return null;

  const valueCount = value[groupId].values?.length || 0;
  const maxValues = getMaxValuesPerGroup();

  return (
    <LimitCounter
      current={valueCount}
      max={maxValues}
      label="Values in Group"
      showAlways={showAlways}
    />
  );
};
