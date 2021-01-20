import { useState } from 'react';

function useFormInputState(defaultValue = '') {
  const [ value, setValue ] = useState(defaultValue);
  const [ error, setError ] = useState('');

  const reset = () => { setValue(defaultValue); setError(''); };
  const onChange = (e) => { setValue(e.target.value); };

  return {
    value, error,
    setValue, setError, reset, onChange
  };
}

export default useFormInputState;
