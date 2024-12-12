/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

import {
  css,
  styled,
  SupersetClient,
  SupersetTheme,
  t,
} from '@superset-ui/core';
import Modal from 'src/components/Modal';
import React, { useEffect, useMemo, useState } from 'react';
import Icons from 'src/components/Icons';
import { LabeledErrorBoundInput } from 'src/components/Form';
import { useSingleViewResource } from 'src/views/CRUD/hooks';
import { TokenObject } from './types';
import InfoTooltip from 'src/components/InfoTooltip';
import { AsyncSelect } from 'src/components';
import rison from 'rison';

const noMargins = css`
  margin: 0;

  .ant-input {
    margin: 0;
  }
`;

const StyledModal = styled(Modal)`
  max-width: 1200px;
  min-width: min-content;
  width: 100%;
  .ant-modal-footer {
    white-space: nowrap;
  }
`;

const StyledIcon = (theme: SupersetTheme) => css`
  margin: auto ${theme.gridUnit * 2}px auto 0;
  color: ${theme.colors.grayscale.base};
`;

const StyledSectionContainer = styled.div`
  display: flex;
  flex-direction: column;
  padding: ${({ theme }) =>
    `${theme.gridUnit * 3}px ${theme.gridUnit * 4}px ${theme.gridUnit * 2}px`};

  label,
  .control-label {
    display: inline-block;
    font-size: ${({ theme }) => theme.typography.sizes.s}px;
    color: ${({ theme }) => theme.colors.grayscale.base};
    vertical-align: middle;
  }

  .info-solid-small {
    vertical-align: middle;
    padding-bottom: ${({ theme }) => theme.gridUnit / 2}px;
  }
`;

const StyledInputContainer = styled.div`
  display: flex;
  flex-direction: column;
  margin: ${({ theme }) => theme.gridUnit}px;
  margin-bottom: ${({ theme }) => theme.gridUnit * 4}px;

  .input-container {
    display: flex;
    align-items: center;

    > div {
      width: 100%;
    }
  }

  input,
  textarea {
    flex: 1 1 auto;
  }

  .required {
    margin-left: ${({ theme }) => theme.gridUnit / 2}px;
    color: ${({ theme }) => theme.colors.error.base};
  }
`;

export interface ExternalTokenModalProps {
  exToken: TokenObject | null;
  addSuccessToast: (msg: string) => void;
  addDangerToast: (msg: string) => void;
  onAdd?: (alert?: any) => void;
  onHide: () => void;
  show: boolean;
}

// * event handlers *
type SelectValue = {
  value: string;
  label: string;
};

const DEFAULT_PAYLOAD = {
  username: '',
  token: '',
  app: '',
  tenant: '',
};

function ExternalTokenModal(props: ExternalTokenModalProps) {
  const { exToken, addDangerToast, addSuccessToast, onHide, show } = props;

  const [currentToken, setCurrentToken] = useState<TokenObject>({
    ...DEFAULT_PAYLOAD,
  });
  const [disableSave, setDisableSave] = useState<boolean>(true);

  const isEditMode = exToken !== null;

  // * hooks *
  const {
    state: { loading, resource, error: fetchError },
    fetchResource,
    createResource,
    updateResource,
    clearError,
  } = useSingleViewResource<TokenObject>(
    `external_token`,
    t('external_token'),
    addDangerToast,
  );

  const updateTokenState = (name: string, value: any) => {
    setCurrentToken(currentTokenData => ({
      ...currentTokenData,
      [name]: value,
    }));
  };

  // * state validators *
  const validate = () => {
    if (
      currentToken?.username &&
      currentToken?.token &&
      currentToken?.app &&
      currentToken?.tenant
    ) {
      setDisableSave(false);
    } else {
      setDisableSave(true);
    }
  };

  // initialize
  useEffect(() => {
    if (!isEditMode) {
      setCurrentToken({ ...DEFAULT_PAYLOAD });
    } else if (exToken?.id && !loading && !fetchError) {
      fetchResource(exToken.id as number);
    }
  }, [exToken]);

  useEffect(() => {
    if (resource) {
      setCurrentToken({ ...resource, id: exToken?.id });
    }
  }, [resource]);

  // validate
  const currentTokenSafe = currentToken || {};
  useEffect(() => {
    validate();
  }, [currentTokenSafe.username, currentTokenSafe.token, currentTokenSafe?.tenant, currentTokenSafe?.app]);

  const onTextChange = (target: HTMLInputElement | HTMLTextAreaElement) => {
    updateTokenState(target.name, target.value);
  };

  
  const onUserChange = (user: Array<SelectValue>) => {
    console.log(user, currentToken)
    updateTokenState('user_id', user || null);
  };

  const hide = () => {
    clearError();
    setCurrentToken({ ...DEFAULT_PAYLOAD });
    onHide();
  };

  const onSave = () => {

    const data: any = { ...currentToken };

    if (isEditMode && currentToken.id) {
      const updateId = currentToken.id;
      delete data.id;
      updateResource(updateId, data).then(response => {
        if (!response) {
          return;
        }
        addSuccessToast(`External Token updated`);
        hide();
      });
    } else if (currentToken) {
      createResource(data).then(response => {
        if (!response) return;
        addSuccessToast(t('External Token added'));
        hide();
      });
    }
  };


  const loadUserOptions = useMemo(
    () =>
      (input = '', page: number, pageSize: number) => {
        const query = rison.encode({
          filter: input,
          page,
          page_size: pageSize,
        });
        return SupersetClient.get({
          endpoint: `/api/v1/security/users/?q=${query}`,
        }).then(response => {
          const list = response.json.result.map(
            (item: { id: number; username: string, first_name: string, last_name: string }) => ({
              label: `${item.first_name} ${item.last_name}`,
              value: item.id,
            }),
          );
          return { data: list, totalCount: response.json.count };
        });
      },
    [],
  );

  return (
    <StyledModal
      className="no-content-padding"
      responsive
      show={show}
      onHide={hide}
      primaryButtonName={isEditMode ? t('Save') : t('Add')}
      disablePrimaryButton={disableSave}
      onHandledPrimaryAction={onSave}
      width="30%"
      maxWidth="1450px"
      title={
        <h4 data-test="rls-modal-title">
          {isEditMode ? (
            <Icons.EditAlt css={StyledIcon} />
          ) : (
            <Icons.PlusLarge css={StyledIcon} />
          )}
          {isEditMode ? t('Edit External Token') : t('Add External Token')}
        </h4>
      }
    >
      <StyledSectionContainer>
        <div className="main-section">
          <StyledInputContainer>
            <div className="control-label">
              {t('Select User')}{' '}
              <InfoTooltip
                tooltip={t(
                  'Select user for syncing role & perms',
                )}
              />
            </div>
            <div className="input-container">
              <AsyncSelect
                ariaLabel={t('Select User')}
                mode="multiple"
                onChange={onUserChange}
                value={(currentToken?.user as SelectValue) || []}
                options={loadUserOptions}
              />
            </div>
          </StyledInputContainer>
          <StyledInputContainer>
            <LabeledErrorBoundInput
              id="username"
              name="username"
              className="labeled-input"
              value={currentToken ? currentToken.username : ''}
              required
              validationMethods={{
                onChange: ({ target }: { target: HTMLInputElement }) =>
                  onTextChange(target),
              }}
              css={noMargins}
              label={t('Username')}
              data-test="et-username-test"
              tooltipText={t('The username of the exToken must be unique')}
              hasTooltip
            />
          </StyledInputContainer>
          <StyledInputContainer>
            <LabeledErrorBoundInput
              id="token"
              name="token"
              className="labeled-input"
              value={currentToken ? currentToken.token : ''}
              required
              validationMethods={{
                onChange: ({ target }: { target: HTMLInputElement }) =>
                  onTextChange(target),
              }}
              css={noMargins}
              label={t('Token')}
              data-test="et-token-test"
              tooltipText={t('The token of the exToken must be unique')}
              hasTooltip
            />
          </StyledInputContainer>
          <StyledInputContainer>
            <LabeledErrorBoundInput
              id="app"
              name="app"
              className="labeled-input"
              value={currentToken ? currentToken.app : ''}
              validationMethods={{
                onChange: ({ target }: { target: HTMLInputElement }) =>
                  onTextChange(target),
              }}
              css={noMargins}
              label={t('App Name')}
              data-test="et-app-test"
              tooltipText={t('The app of the exToken must be not null')}
              hasTooltip
            />
          </StyledInputContainer>
          <StyledInputContainer>
            <LabeledErrorBoundInput
              id="tenant"
              name="tenant"
              className="labeled-input"
              value={currentToken ? currentToken.tenant : ''}
              validationMethods={{
                onChange: ({ target }: { target: HTMLInputElement }) =>
                  onTextChange(target),
              }}
              css={noMargins}
              label={t('Tenant Name')}
              data-test="et-tenant-test"
              tooltipText={t('The tenant of the exToken must be not null')}
              hasTooltip
            />
          </StyledInputContainer>
        </div>
      </StyledSectionContainer>
    </StyledModal>
  );
}

export default ExternalTokenModal;
